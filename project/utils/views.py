import abc
import logging

from django.apps import apps
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView
from django.views.generic.edit import DeleteView, UpdateView, CreateView

from assessment.models import Assessment, TimeSpentEditing
from .helper import tryParseInt


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
        return super().delete(request, *args, **kwargs)

    def form_valid(self, form):
        self.send_message()
        return super().form_valid(form)


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
        return super().dispatch(request, *args, **kwargs)


class AssessmentPermissionsMixin(object):
    """
    Mixin to check permissions for an object of interest to determine if a user
    is able to view and delete the object. Will return an object or issue an
    HTTP 403 error. Will also return a set of template tags {{ obj_perms }}
    for displaying page. Note that this for all objects which are controlled
    by the assessment object but not including the assessment object.
    """
    def deny_for_locked_study(self, user, assessment, obj):
        # determine relevant study for a given object, and then checks its editable status.
        # If not set, raises a PermissionDenied.
        study_editability = self.check_study_editability(user, assessment, obj)
        if study_editability is not None:
            if study_editability is False:
                raise PermissionDenied

    def check_study_editability(self, user, assessment, obj):
        # TODO - investigate refactoring only in the case where an object is being mutated; not read
        # (will reduce db query load for getting study for all objects)
        # TODO - add unit tests
        # retrieve the related study from this instance
        # could also do this by defining some kind of base class that Study, Experiment, etc.
        # inherit from, and define the get_study method on there. Then we just
        # check an "is-a" instead of looking for the attribute manually.
        study = None
        study_fetch_method = getattr(obj, 'get_study', None)
        if callable(study_fetch_method):
            study = study_fetch_method()

        if assessment.user_can_edit_object(user):
            if study is not None:
                if study.user_can_edit_study(assessment, user):
                    return True
                else:
                    return False
            return None
        else:
            return False

    # could be a model element (Study, Endpoint, etc.) or a view to create a new one (EndpointCreate, etc.)
    def get_contextual_object_for_study_editability_check(self):
        if hasattr(self, "object") and self.object is not None:
            # looking at a specific object directly
            return self.object
        elif hasattr(self, "parent") and self.parent is not None:
            # looking at a Create view; can look at the parent/container object to determine study editable status
            return self.parent
        else:
            return None

    def permission_check_user_can_view(self):
        logging.debug('Permissions checked')
        if not self.assessment.user_can_view_object(self.request.user):
            raise PermissionDenied

    def permission_check_user_can_edit(self):
        logging.debug('Permissions checked')
        if self.model == Assessment:
            canEdit = self.assessment.user_can_edit_assessment(self.request.user)
        else:
            self.deny_for_locked_study(self.request.user, self.assessment, self.get_contextual_object_for_study_editability_check())
            canEdit = self.assessment.user_can_edit_object(self.request.user)
        if not canEdit:
            raise PermissionDenied

    def get_object(self, **kwargs):
        """
        Check to make sure user can view object
        """
        obj = kwargs.get('object')
        if not obj:
            obj = super().get_object(**kwargs)

        if not hasattr(self, 'assessment'):
            self.assessment = obj.get_assessment()

        if self.crud == 'Read':
            perms = self.assessment.user_can_view_object(self.request.user)
        else:
            if self.model == Assessment:
                perms = self.assessment.user_can_edit_assessment(self.request.user)
            else:
                self.deny_for_locked_study(self.request.user, self.assessment, obj)
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
        queryset = super().get_queryset()
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
                    self.deny_for_locked_study(self.request.user, self.assessment, obj)
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
        user_perms = self.assessment.user_permissions(self.request.user)

        contextual_obj = self.get_contextual_object_for_study_editability_check()
        study_perm_check = self.check_study_editability(self.request.user, self.assessment, contextual_obj)
        if study_perm_check is not None:
            user_perms['edit'] = study_perm_check

        return user_perms


class TimeSpentOnPageMixin(object):

    def get(self, request, *args, **kwargs):
        TimeSpentEditing.set_start_time(
            self.request.session.session_key,
            self.request.path,
        )
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        response = super().get_success_url()
        TimeSpentEditing.add_time_spent_job(
            self.request.session.session_key,
            self.request.path,
            self.object,
            self.assessment.id
        )
        return response


class ProjectManagerOrHigherMixin(object):
    """
    Mixin for project-manager access to page.
    Requires a get_assessment method; checked for all HTTP verbs.
    """

    @abc.abstractmethod
    def get_assessment(self, request, *args, **kwargs):
        raise NotImplementedError('get_assessment requires implementation')

    def dispatch(self, request, *args, **kwargs):
        self.assessment = self.get_assessment(request, *args, **kwargs)
        logging.debug("Permissions checked")
        if not self.assessment.user_can_edit_assessment(request.user):
            raise PermissionDenied
        return super()\
            .dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super()\
            .get_context_data(**kwargs)
        context['assessment'] = self.assessment
        return context


class TeamMemberOrHigherMixin(object):
    """
    Mixin for team-member access to page.
    Requires a get_assessment method; checked for all HTTP verbs.
    """

    @abc.abstractmethod
    def get_assessment(self, request, *args, **kwargs):
        raise NotImplementedError('get_assessment requires implementation')

    def dispatch(self, request, *args, **kwargs):
        self.assessment = self.get_assessment(request, *args, **kwargs)
        logging.debug("Permissions checked")
        if not self.assessment.user_can_edit_object(request.user):
            raise PermissionDenied
        return super()\
            .dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super()\
            .get_context_data(**kwargs)
        context['assessment'] = self.assessment
        return context


class IsAuthorMixin(object):
    # Throw error if user is not author

    owner_field = 'author'

    def get_object(self):
        obj = super().get_object()
        if getattr(obj, self.owner_field) != self.request.user:
            raise PermissionDenied
        return obj


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
            return super().get(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def post(self, request, *args, **kwargs):
        if self.user_can_create_object(self.assessment):
            return super().post(request, *args, **kwargs)
        else:
            raise PermissionDenied


class CopyAsNewSelectorMixin(object):
    form_class = None  # required
    copy_model = None  # required
    template_name_suffix = '_copy_selector'

    def get_related_id(self):
        return self.object.id

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # prevents copy from locked studies
        if context['obj_perms']['edit'] is False:
            raise PermissionDenied

        related_id = self.get_related_id()
        context['form'] = self.form_class(parent_id=related_id)
        return context

    def get_template_names(self):
        if self.template_name is not None:
            name = self.template_name
        else:
            name = '%s/%s%s.html' % (
                self.copy_model._meta.app_label,
                self.copy_model._meta.object_name.lower(),
                self.template_name_suffix
            )
        return [name]


# Base HAWC views
class BaseDetail(AssessmentPermissionsMixin, DetailView):
    crud = 'Read'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assessment'] = self.assessment
        context['crud'] = self.crud
        context['obj_perms'] = super().get_obj_perms()
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
        context = super().get_context_data(**kwargs)
        context['assessment'] = self.assessment
        context['crud'] = self.crud
        context['obj_perms'] = super().get_obj_perms()
        return context


class BaseUpdate(TimeSpentOnPageMixin, AssessmentPermissionsMixin, MessageMixin, UpdateView):
    crud = 'Update'

    def form_valid(self, form):
        self.object = form.save()
        self.post_object_save(form)  # add hook for post-object save
        self.send_message()
        return HttpResponseRedirect(self.get_success_url())

    def post_object_save(self, form):
        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assessment'] = self.assessment
        context['crud'] = self.crud
        context['obj_perms'] = super().get_obj_perms()
        return context


class BaseCreate(TimeSpentOnPageMixin, AssessmentPermissionsMixin, MessageMixin, CreateView):
    parent_model = None  # required
    parent_template_name = None  # required
    crud = 'Create'

    def dispatch(self, *args, **kwargs):
        self.parent = get_object_or_404(self.parent_model, pk=kwargs['pk'])
        self.assessment = self.parent.get_assessment()
        self.permission_check_user_can_edit()
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # all inputs require a parent field
        kwargs['parent'] = self.parent

        # check if we have an object-template to be used
        pk = tryParseInt(self.request.GET.get('initial'), -1)

        if pk > 0:
            initial = self.model.objects.filter(pk=pk).first()
            if initial and initial.get_assessment() in \
                    Assessment.objects.get_viewable_assessments(self.request.user, public=True):
                kwargs['initial'] = model_to_dict(initial)

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['crud'] = self.crud
        context['assessment'] = self.assessment
        context['obj_perms'] = super().get_obj_perms()
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
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assessment'] = self.assessment
        context['obj_perms'] = super().get_obj_perms()
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
        context = super().get_context_data(**kwargs)
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
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['formset'] = self.build_initial_formset_factory()
        else:
            if kwargs.get('form'):
                context['form'] = kwargs.get('form')
            if kwargs.get('formset'):
                context['formset'] = kwargs.get('formset')
        return context


class BaseEndpointFilterList(BaseList):
    parent_model = Assessment
    form_class = None  # required

    def get_paginate_by(self, qs):
        val = 25
        try:
            val = int(self.request.GET.get('paginate_by', val))
        except ValueError:
            pass
        return val

    def get(self, request, *args, **kwargs):
        if len(self.request.GET) > 0:
            self.form = self.form_class(
                self.request.GET,
                assessment=self.assessment
            )
        else:
            self.form = self.form_class(
                assessment=self.assessment
            )
        return super().get(request, *args, **kwargs)

    def get_query(self, perms):
        """
        query = Q(relation__to__assessment=self.assessment)
        if not perms['edit']:
            query &= Q(study__published=True)
        return query
        """
        pass

    def get_queryset(self):
        perms = super().get_obj_perms()
        order_by = None

        query = self.get_query(perms)

        if self.form.is_valid():
            query &= self.form.get_query()
            order_by = self.form.get_order_by()

        ids = self.model.objects.filter(query)\
            .order_by('id')\
            .distinct('id')\
            .values_list('id', flat=True)

        qs = self.model.objects.filter(id__in=ids)

        if order_by:
            qs = qs.order_by(order_by)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        context['list_json'] = self.model.get_qs_json(
            context['object_list'], json_encode=True)
        return context
