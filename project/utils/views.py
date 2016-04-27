import abc
import os
import logging
import celery

from django.conf import settings
from django.shortcuts import HttpResponse
from django.apps import apps
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import get_object_or_404, Http404
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.generic import DetailView, ListView
from django.views.generic.edit import DeleteView, UpdateView, CreateView

from assessment.models import Assessment


class MessageMixin(object):
    """
    Make it easy to display notification messages when using Class Based Views.
    Originally from http://stackoverflow.com/questions/5531258/
    """
    def send_message(self):
        logging.debug('MessagingMixin called')
        if self.success_message is not None:
            messages.success(self.request, self.success_message, extra_tags='alert alert-success')

    def delete(self, request, *args, **kwargs):
        self.send_message()
        return super(MessageMixin, self).delete(request, *args, **kwargs)

    def form_valid(self, form):
        self.send_message()
        return super(MessageMixin, self).form_valid(form)


class CloseIfSuccessMixin(object):
    """
    Mixin designed to close-window if form executes successfully.
    """
    def get_success_url(self):
        return reverse("assessment:close_window")


class LoginRequiredMixin(object):
    """
    A mixin requiring a user to be logged in.
    """
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class AssessmentPermissionsMixin(object):
    """
    Mixin to check permissions for an object of interest to determine if a user
    is able to view and delete the object. Will return an object or issue an
    HTTP 403 error. Will also return a set of template tags {{ obj_perms }}
    for displaying page. Note that this for all objects which are controlled
    by the assessment object but not including the assessment object.
    """

    def permission_check_user_can_view(self):
        logging.debug('Permissions checked')
        if not self.assessment.user_can_view_object(self.request.user):
            raise PermissionDenied

    def permission_check_user_can_edit(self):
        logging.debug('Permissions checked')
        if self.model == Assessment:
            canEdit = self.assessment.user_can_edit_assessment(self.request.user)
        else:
            canEdit = self.assessment.user_can_edit_object(self.request.user)
        if not canEdit:
            raise PermissionDenied

    def get_object(self, **kwargs):
        """
        Check to make sure user can view object
        """
        obj = kwargs.get('object')
        if not obj:
            obj = super(AssessmentPermissionsMixin, self).get_object(**kwargs)

        if not hasattr(self, 'assessment'):
            self.assessment = obj.get_assessment()

        if self.crud == 'Read':
            perms = self.assessment.user_can_view_object(self.request.user)
        else:
            if self.model == Assessment:
                perms = self.assessment.user_can_edit_assessment(self.request.user)
            else:
                perms = self.assessment.user_can_edit_object(self.request.user)

        logging.debug('Permissions checked')
        if perms:
            return obj
        else:
            raise PermissionDenied

    def get_queryset(self):
        """
        IF attempting to use for permissions checking, requires a
        self.assessment parameter in class with the assessment to check
        permissions for.
        """
        queryset = super(AssessmentPermissionsMixin, self).get_queryset()
        if not hasattr(self, 'assessment'):
            # get_object calls get_queryset; thus we must be careful to check
            # the correct object
            return queryset
        else:
            # IF, the view has a self.assessment identified, this will check
            # to ensure that a user is allowed to perform the selected actions.
            #
            # TODO: might be preferred to check the get_assessment function with
            # a user, and ensure that get_assessment is called for ALL models
            # with assessment permissions mixin
            #
            if self.crud == 'Read':
                perms = self.assessment.user_can_view_object(self.request.user)
            else:
                if self.model == Assessment:
                    perms = self.assessment.user_can_edit_assessment(self.request.user)
                else:
                    perms = self.assessment.user_can_edit_object(self.request.user)
            logging.debug('Permissions checked')
            if perms:
                return queryset
            else:
                raise PermissionDenied

    def get_obj_perms(self):
        if not hasattr(self, 'assessment'):
            logging.error('unable to determine object permissions')
            return {'view': False, 'edit': False, 'edit_assessment': False}

        logging.debug('Permissions added')
        return self.assessment.user_permissions(self.request.user)


class ProjectManagerOrHigherMixin(object):
    """
    Mixin for project-manager access to page.
    Requires a get_assessment method; checked for all HTTP verbs.
    """

    @abc.abstractmethod
    def get_assessment(self, request, *args, **kwargs):
        pass

    def dispatch(self, request, *args, **kwargs):
        self.assessment = self.get_assessment(request, *args, **kwargs)
        logging.debug("Permissions checked")
        if not self.assessment.user_can_edit_assessment(request.user):
            raise PermissionDenied
        return super(ProjectManagerOrHigherMixin, self)\
            .dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProjectManagerOrHigherMixin, self)\
            .get_context_data(**kwargs)
        context['assessment'] = self.assessment
        return context


class TeamMemberOrHigherMixin(object):
    """
    Mixin for team-member access to page.
    Requires a get_assessment method; checked for all HTTP verbs.
    """
    model = Assessment

    @abc.abstractmethod
    def get_assessment(self, request, *args, **kwargs):
        pass

    def dispatch(self, request, *args, **kwargs):
        self.assessment = self.get_assessment(request, *args, **kwargs)
        logging.debug("Permissions checked")
        if not self.assessment.user_can_edit_object(request.user):
            raise PermissionDenied
        return super(TeamMemberOrHigherMixin, self)\
            .dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TeamMemberOrHigherMixin, self)\
            .get_context_data(**kwargs)
        context['assessment'] = self.assessment
        return context


class CanCreateMixin(object):
    """
    Checks to make sure that the user has appropriate permissions before adding
    a new object to the assessment. Requires a self.assessment variable to be
    created before rendering.
    """

    def user_can_create_object(self, assessment):
        """
        If person is superuser or assessment is editable and user is a project
        manager or team member.
        """
        logging.debug('Permissions checked')
        if self.request.user.is_superuser:
            return True
        elif self.request.user.is_anonymous():
            return False
        else:
            return ((assessment.editable is True) and
                    ((self.request.user in assessment.project_manager.all()) or
                     (self.request.user in assessment.team_members.all())))

    def get(self, request, *args, **kwargs):
        if self.user_can_create_object(self.assessment):
            return super(CanCreateMixin, self).get(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def post(self, request, *args, **kwargs):
        if self.user_can_create_object(self.assessment):
            return super(CanCreateMixin, self).post(request, *args, **kwargs)
        else:
            raise PermissionDenied


# Base HAWC views
class BaseDetail(AssessmentPermissionsMixin, DetailView):
    crud = 'Read'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['assessment'] = self.assessment
        context['crud'] = self.crud
        context['obj_perms'] = super(BaseDetail, self).get_obj_perms()
        return context


class BaseDelete(AssessmentPermissionsMixin, MessageMixin, DeleteView):
    crud = 'Delete'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.permission_check_user_can_edit()
        success_url = self.get_success_url()
        self.object.delete()
        self.send_message()
        return HttpResponseRedirect(success_url)

    def get_context_data(self, **kwargs):
        context = super(DeleteView, self).get_context_data(**kwargs)
        context['assessment'] = self.assessment
        context['crud'] = self.crud
        context['obj_perms'] = super(BaseDelete, self).get_obj_perms()
        return context


class BaseVersion(BaseDetail):
    crud = 'Update'  # requires edit-level permissions to view

    def get_context_data(self, **kwargs):
        context = super(BaseVersion, self).get_context_data(**kwargs)
        context['versions'] = self.object.get_prior_versions_json()
        return context


class BaseUpdate(AssessmentPermissionsMixin, MessageMixin, UpdateView):
    crud = 'Update'

    def form_valid(self, form):
        self.object = form.save()
        self.post_object_save(form)  # add hook for post-object save
        self.send_message()
        return HttpResponseRedirect(self.get_success_url())

    def post_object_save(self, form):
        pass

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['assessment'] = self.assessment
        context['crud'] = self.crud
        context['obj_perms'] = super(BaseUpdate, self).get_obj_perms()
        return context


class BaseCreate(AssessmentPermissionsMixin, MessageMixin, CreateView):
    parent_model = None  # required
    parent_template_name = None  # required
    crud = 'Create'

    def dispatch(self, *args, **kwargs):
        self.parent = get_object_or_404(self.parent_model, pk=kwargs['pk'])
        self.assessment = self.parent.get_assessment()
        self.permission_check_user_can_edit()
        return super(BaseCreate, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(BaseCreate, self).get_form_kwargs()

        # all inputs require a parent field
        kwargs['parent'] = self.parent

        # check if we have an object-template to be used
        try:
            pk = int(self.request.GET.get('initial', -1))
        except ValueError:
            pk = -1

        if pk > 0:
            initial = self.model.objects.filter(pk=pk).first()
            if initial and initial.get_assessment() in \
                    Assessment.get_viewable_assessments(self.request.user, public=True):
                kwargs['initial'] = model_to_dict(initial)

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(BaseCreate, self).get_context_data(**kwargs)
        context['crud'] = self.crud
        context['assessment'] = self.assessment
        context['obj_perms'] = super(BaseCreate, self).get_obj_perms()
        context[self.parent_template_name] = self.parent
        return context

    def form_valid(self, form):
        self.object = form.save()
        self.post_object_save(form)  # add hook for post-object save
        self.send_message()
        return HttpResponseRedirect(self.get_success_url())

    def post_object_save(self, form):
        pass


class BaseList(AssessmentPermissionsMixin, ListView):
    """
    Basic view that shows a list of objects given
    """
    parent_model = None  # required
    parent_template_name = None  # optional
    crud = 'Read'

    def dispatch(self, *args, **kwargs):
        self.parent = get_object_or_404(self.parent_model, pk=kwargs['pk'])
        self.assessment = self.parent.get_assessment()
        self.permission_check_user_can_view()
        return super(BaseList, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BaseList, self).get_context_data(**kwargs)
        context['assessment'] = self.assessment
        context['obj_perms'] = super(BaseList, self).get_obj_perms()
        context['crud'] = self.crud
        if self.parent_template_name:
            context[self.parent_template_name] = self.parent
        return context


class BaseCreateWithFormset(BaseCreate):
    """
    Create view with both a single form and formset. Adds three new options:

    - formset_factory: required to load POST data into factory. Formset factory method.
    - post_object_save: method for modifying formset after form is saved but before formset. No return.
    - build_initial_formset_factory: method for returning initial formset factory. Returns formset_factory
    """
    formset_factory = None   # required

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset = self.formset_factory(data=self.request.POST, **self.get_formset_kwargs())
        self.pre_validate(form, formset)
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def get_formset_kwargs(self):
        return {}

    def form_valid(self, form, formset):
        self.object = form.save()
        self.post_object_save(form, formset)
        formset.save()
        self.post_formset_save(form, formset)
        self.send_message()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def get_context_data(self, **kwargs):
        context = super(BaseCreateWithFormset, self).get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['formset'] = self.build_initial_formset_factory()
        else:
            if kwargs.get('form'):
                context['form'] = kwargs.get('form')
            if kwargs.get('formset'):
                context['formset'] = kwargs.get('formset')
        return context

    def pre_validate(self, form, formset):
        pass

    def post_object_save(self, form, formset):
        pass

    def post_formset_save(self, form, formset):
        pass

    def build_initial_formset_factory(self):
        # Returns initial formset factory
        raise NotImplementedError("Method should be overridden to return a formset factory")


class BaseUpdateWithFormset(BaseUpdate):
    """
    Update view with both a single form and formset. Adds three new options:

    - formset_factory: required to load POST data into factory. Formset factory method.
    - post_objet_save: method for modifying formset after form is saved but before formset. No return.
    - build_initial_formset_factory: method for returning initial formset factory. Returns formset_factory
    """
    formset_factory = None   # required

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset = self.formset_factory(data=self.request.POST, **self.get_formset_kwargs())
        self.pre_validate(form, formset)
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def get_formset_kwargs(self):
        return {}

    def form_valid(self, form, formset):
        self.object = form.save()
        self.post_object_save(form, formset)
        formset.save()
        self.post_formset_save(form, formset)
        self.send_message()
        return HttpResponseRedirect(self.get_success_url())

    def pre_validate(self, form, formset):
        pass

    def post_object_save(self, form, formset):
        pass

    def post_formset_save(self, form, formset):
        pass

    def form_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(
                                       form=form, formset=formset))

    def build_initial_formset_factory(self):
        # Returns initial formset factory
        raise NotImplementedError("Method should be overridden to return a formset factory")

    def get_context_data(self, **kwargs):
        context = super(BaseUpdateWithFormset, self).get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['formset'] = self.build_initial_formset_factory()
        else:
            if kwargs.get('form'):
                context['form'] = kwargs.get('form')
            if kwargs.get('formset'):
                context['formset'] = kwargs.get('formset')
        return context


class GenerateReport(BaseList):
    """
    Generate a docx report given an assessment, data-type, and template.
    """
    report_type = None  # required; refer to assessment.ReportTemplate report-type choices

    def get_filename(self):
        raise NotImplementedError("Requires String return for docx filename")

    def get_context(self, queryset):
        raise NotImplementedError("Requires dictionary return for mail-merge")

    def get_template(self, request):
        ReportTemplate = apps.get_model("assessment", "ReportTemplate")
        try:
            template_id = request.GET.get('template_id', -1)
            return ReportTemplate.get_template(template_id, self.assessment.id, self.report_type)
        except ObjectDoesNotExist:
            raise Http404

    def get(self, request, *args, **kwargs):
        self.onlyPublished = bool(self.request.GET.get('onlyPublished', False))
        self.object_list = self.get_queryset()
        template = self.get_template(request)
        context = self.get_context(self.object_list)
        filename = self.get_filename()
        return template.apply_mailmerge(context, filename)


class GenerateFixedReport(BaseList):
    """
    Generate a docx report given an assessment, data-type, using method as template.
    """
    ReportClass = None  # required; class used to generate report

    def get_context(self, queryset):
        raise NotImplementedError("Requires report-context object")

    def get_filename(self):
        raise NotImplementedError("Requires dictionary return for mail-merge")

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context(self.object_list)
        filename = self.get_filename()
        root_path = os.path.join(settings.PROJECT_PATH, 'templates', 'hawc')
        report = self.ReportClass(root_path, context)
        try:
            task = self.getResponse.delay(self, report, filename)
            response = task.get(timeout=120)
        except celery.exceptions.TimeoutError:
            response = HttpResponseServerError("<p>An error in processing occurred - report not generated.</p>")
        return response

    @celery.shared_task
    def getResponse(self, report, filename):
        response = HttpResponse(report.build_report())
        response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        return response
