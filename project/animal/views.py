import json

from django.core.exceptions import PermissionDenied
from django.forms.models import inlineformset_factory
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView

from assessment.models import Assessment
from study.models import Study
from utils.forms import form_error_list_to_ul
from utils.helper import HAWCDjangoJSONEncoder
from utils.views import (MessageMixin, CanCreateMixin,
                         AssessmentPermissionsMixin, CloseIfSuccessMixin,
                         BaseCreate, BaseDelete, BaseDetail, BaseUpdate, BaseList,
                         BaseVersion)
from utils.helper import HAWCdocx

from . import forms
from . import models


# Experiment Views
class ExperimentCreate(BaseCreate):
    success_message = 'Experiment created.'
    parent_model = Study
    parent_template_name = 'study'
    model = models.Experiment
    form_class = forms.ExperimentForm

    def dispatch(self, *args, **kwargs):
        response = super(ExperimentCreate, self).dispatch(*args, **kwargs)
        if self.parent.get_study_type_display() != "Animal Bioassay":
            raise Http404
        return response


class ExperimentRead(BaseDetail):
    model = models.Experiment

    def get_context_data(self, **kwargs):
        context = super(ExperimentRead, self).get_context_data(**kwargs)
        context['comment_object_type'] = "experiment"
        context['comment_object_id'] = self.object.pk
        return context


class ExperimentUpdate(BaseUpdate):
    success_message = "Experiment updated."
    model = models.Experiment
    form_class = forms.ExperimentForm


class ExperimentDelete(BaseDelete):
    success_message = "Experiment deleted."
    model = models.Experiment

    def get_success_url(self):
        return self.object.study.get_absolute_url()


# Animal Group Views
class AnimalGroupCreate(CanCreateMixin, MessageMixin, CreateView):
    """
    Create view of AnimalGroup. Either creates a AnimalGroup, or a
    GenerationalAnimalGroup, depending on if the experiment is deemed a
    generational experiment.
    """
    model = models.AnimalGroup
    template_name = "animal/animalgroup_form.html"
    form_class = forms.AnimalGroupForm
    success_message = "Animal Group created."
    crud = "Create"

    def dispatch(self, *args, **kwargs):
        self.experiment = get_object_or_404(models.Experiment, pk=kwargs['pk'])
        if self.experiment.is_generational():
            self.model = models.GenerationalAnimalGroup
            self.form_class = forms.GenerationalAnimalGroupForm
        self.assessment = self.experiment.get_assessment()
        return super(AnimalGroupCreate, self).dispatch(*args, **kwargs)

    def get_form(self, form_class):
        form = super(AnimalGroupCreate, self).get_form(form_class)
        form.fields['siblings'].queryset = models.AnimalGroup.objects.filter(
                experiment=self.experiment.pk)
        if form_class == forms.GenerationalAnimalGroupForm:
            form.fields['parents'].queryset = models.AnimalGroup.objects.filter(
                    experiment=self.experiment.pk)
            form.fields['dosing_regime'].queryset = models.DosingRegime.objects.filter(
                dosed_animals__in=form.fields['parents'].queryset)
        return form

    def get_form_kwargs(self):
        kwargs = super(CreateView, self).get_form_kwargs()
        kwargs['parent'] = self.experiment
        return kwargs

    def form_valid(self, form):
        """
        Complicated logic here. If an animal group is NOT generational, then it
        requires its own dosing regime. Thus, we must make sure the dosing regime
        is valid before attempting to save.

        If an animal group IS generational, a dosing-regime can be specified
        from parent groups. OR, a dosing-regime can be created.
        """
        self.object = form.save(commit=False)

        #allow a shortcut for specified dosing-regime
        if issubclass(self.model, models.GenerationalAnimalGroup) and self.object.dosing_regime:
            #save animal-group
            self.object.save()

            # Save generational animal-group m2m information as well
            if issubclass(self.model, models.GenerationalAnimalGroup):
                for parent in form.cleaned_data['parents']:
                    self.object.parents.add(parent.generationalanimalgroup)

            self.send_message()
            return HttpResponseRedirect(self.get_success_url())

        # Otherwise, we'll need to ensure the dosing-regime is appropriate
        # Check if dosing-regime is also valid
        self.form_dosing_regime = forms.DosingRegimeForm(self.request.POST)
        if self.form_dosing_regime.is_valid():
            dosing_regime = self.form_dosing_regime.save(commit=False)

            #now, try to save each dose-group
            dose_groups = json.loads(self.request.POST['dose_groups_json'])
            try:
                models.DoseGroup.clean_formset(dose_groups, dosing_regime.num_dose_groups)
            except ValidationError as e:
                self.dose_groups_errors = e.messages[0]
                return self.form_invalid(form)

            dose_group_objects = []
            for dose_group in dose_groups:  # todo: make sure doses are ascending
                dose_group_form = forms.DoseGroupForm(dose_group)
                if dose_group_form.is_valid():
                    dose_group_objects.append(dose_group_form.save(commit=False))
                else:
                    self.dose_groups_errors = form_error_list_to_ul(dose_group_form)
                    return self.form_invalid(form)

            #OK, everything is valid. Let's start saving to the database.

            """
            First, we'll save the dosing regime. Then, we'll associate this
            dosing regime with the animal-group. Next, we'll save the
            dosed_animals equal to this animal-group.
            """
            dosing_regime.save()
            self.object.dosing_regime = dosing_regime
            self.object.save()
            dosing_regime.dosed_animals = self.object
            dosing_regime.save()

            # Save generational animal-group m2m information as well
            if issubclass(self.model, models.GenerationalAnimalGroup):
                for parent in form.cleaned_data['parents']:
                    self.object.parents.add(parent.generationalanimalgroup)

            # Save doses
            for obj in dose_group_objects:
                obj.dose_regime = dosing_regime
            models.DoseGroup.objects.bulk_create(dose_group_objects)

            self.send_message()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context["crud"] = self.crud
        context["experiment"] = self.experiment
        context["assessment"] = self.assessment
        context["dose_types"] = models.DoseUnits.json_all()
        if hasattr(self, 'form_dosing_regime'):
            context['form_dosing_regime'] = self.form_dosing_regime
        else:
            context["form_dosing_regime"] = forms.DosingRegimeForm()

        if self.request.method == 'POST':  # send back dose-group errors
            context['dose_groups_json'] = self.request.POST['dose_groups_json']
            if hasattr(self, 'dose_groups_errors'):
                context['dose_groups_errors'] = self.dose_groups_errors

        return context


class AnimalGroupRead(BaseDetail):
    model = models.AnimalGroup

    def get_context_data(self, **kwargs):
        context = super(AnimalGroupRead, self).get_context_data(**kwargs)
        context['comment_object_type'] = "animal_group"
        context['comment_object_id'] = self.object.pk
        return context


class AnimalGroupUpdate(AssessmentPermissionsMixin, MessageMixin, UpdateView):
    """
    Update selected experiment.
    """
    model = models.AnimalGroup
    template_name = "animal/animalgroup_form.html"
    form_class = forms.AnimalGroupForm
    success_message = "Animal Group updated."
    crud = "Update"

    def get_object(self, queryset=None):
        obj = super(AnimalGroupUpdate, self).get_object()
        self.dosing_regime = obj.dosing_regime # part of HACK below
        if obj.experiment.is_generational():
            self.model = models.GenerationalAnimalGroup
            self.form_class = forms.GenerationalAnimalGroupForm
            return obj.generationalanimalgroup
        return obj

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context["crud"] = self.crud
        context["assessment"] = context["object"].get_assessment()
        context["dose_types"] = models.DoseUnits.json_all()
        context['form_dosing_regime'] = forms.DosingRegimeForm(instance=self.object.dosing_regime)

        if self.request.method == 'POST':  # send back dose-group errors
            context['dose_groups_json'] = self.request.POST['dose_groups_json']
            if hasattr(self, 'form_dosing_regime'):
                context['form_dosing_regime'] = self.form_dosing_regime
            if hasattr(self, 'dose_groups_errors'):
                context['dose_groups_errors'] = self.dose_groups_errors
        else:
            context['dose_groups_json'] = self.object.dosing_regime.get_dose_groups_for_animal_form()

        return context

    def get_form(self, form_class):
        form = super(AnimalGroupUpdate, self).get_form(form_class)
        form.fields['siblings'].queryset = models.AnimalGroup.objects.filter(
                    experiment=self.object.experiment.pk).exclude(pk=self.object.pk)
        form.fields['strain'].queryset = models.Strain.objects.filter(species=self.object.species)
        if form_class == forms.GenerationalAnimalGroupForm:
            form.fields['parents'].queryset = models.AnimalGroup.objects.filter(
                    experiment=self.object.experiment.pk).exclude(pk=self.object.pk)
            form.fields['dosing_regime'].queryset = models.DosingRegime.objects.filter(
                dosed_animals__in=models.AnimalGroup.objects.filter(experiment=self.object.experiment.pk))
        return form

    def form_valid(self, form):
        """
        Make sure that everything is valid before attempting to re-save or update anything
        """
        self.object = form.save(commit=False)
        self.object.dosing_regime = self.dosing_regime  # return to original regardless of form changes # HACK

        #allow a shortcut for specified dosing-regime
        if ((issubclass(self.model, models.GenerationalAnimalGroup)) and
                (self.object.dosing_regime.dosed_animals.pk != self.object.pk)):
            #save animal-group
            self.object.save()

            # Save generational animal-group m2m information as well
            if issubclass(self.model, models.GenerationalAnimalGroup):
                for parent in form.cleaned_data['parents']:
                    self.object.parents.add(parent.generationalanimalgroup)

            self.send_message()
            return HttpResponseRedirect(self.get_success_url())

        # Otherwise, we'll need to ensure the dosing-regime is appropriate
        # Check if dosing-regime is also valid
        try:
            self.form_dosing_regime = forms.DosingRegimeForm(self.request.POST,
                    instance=self.object.dosing_regime)
        except:
            self.form_dosing_regime = forms.DosingRegimeForm(self.request.POST)

        if self.form_dosing_regime.is_valid():
            dosing_regime = self.form_dosing_regime.save(commit=False)

            #now, try to save each dose-group
            dose_groups = json.loads(self.request.POST['dose_groups_json'])
            try:
                models.DoseGroup.clean_formset(dose_groups, dosing_regime.num_dose_groups)
            except ValidationError as e:
                self.dose_groups_errors = e.messages[0]
                return self.form_invalid(form)

            dose_group_objects = []
            for dose_group in dose_groups:  # todo: make sure doses are ascending
                try:
                    dose_group_form = forms.DoseGroupForm(dose_group,
                        instance=models.DoseGroup.objects.get(dose_regime=dosing_regime.pk,
                            dose_units=dose_group['dose_units'],
                            dose_group_id=dose_group['dose_group_id']))
                except:
                    dose_group_form = forms.DoseGroupForm(dose_group)
                if dose_group_form.is_valid():
                    dose_group_objects.append(dose_group_form.save(commit=False))
                else:
                    self.dose_groups_errors = form_error_list_to_ul(dose_group_form)
                    return self.form_invalid(form)

            #OK, everything is valid. Let's start saving to the database.

            """
            First, we'll save the dosing regime. Then, we'll associate this
            dosing regime with the animal-group. Next, we'll save the
            dosed_animals equal to this animal-group.
            """
            dosing_regime.save()
            self.object.dosing_regime = dosing_regime
            self.object.save()
            dosing_regime.dosed_animals = self.object
            dosing_regime.save()

            # Save generational animal-group m2m information as well
            if issubclass(self.model, models.GenerationalAnimalGroup):
                for parent in form.cleaned_data['parents']:
                    self.object.parents.add(parent.generationalanimalgroup)

            # Save doses
            for obj in dose_group_objects:
                obj.dose_regime = dosing_regime
                obj.save()

            #Delete any additional doses
            pks = [obj.pk for obj in dose_group_objects]
            models.DoseGroup.objects.filter(dose_regime=dosing_regime.pk)\
                                    .exclude(pk__in=pks).delete()

            self.send_message()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)


class AnimalGroupDelete(BaseDelete):
    success_message = "Animal-group deleted."
    model = models.AnimalGroup

    def get_success_url(self):
        return self.object.experiment.get_absolute_url()


# Dosing Regime Views
class DosingRegimeCreate(CanCreateMixin, MessageMixin, CreateView):
    """
    Create view of Dosing Regime. Has custom logic to also add dose-groups with
    each creation of a dose-regime.
    """
    model = models.DosingRegime
    form_class = forms.DosingRegimeForm
    success_message = "Dosing regime created."
    crud = "Create"

    def dispatch(self, *args, **kwargs):
        self.animal_group = get_object_or_404(models.AnimalGroup, pk=kwargs['pk'])
        self.assessment = self.animal_group.get_assessment()
        return super(DosingRegimeCreate, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.user_can_create_object(self.assessment):
            raise PermissionDenied
        #first, try to save dosing-regime
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            self.object = form.save(commit=False)
            self.object.dosed_animals = self.animal_group
            self.object.save()
            #now, try to save each dose-group
            dose_groups = json.loads(request.POST['dose_groups_json'])

            try:
                models.DoseGroup.clean_formset(dose_groups, self.object.num_dose_groups)
            except ValidationError as e:
                self.dose_groups_errors = e.messages[0]
                self.object.delete()
                return self.form_invalid(form)

            for dose_group in dose_groups:  # todo: make sure ascending order
                dose_group['dose_regime'] = self.object.pk
                dose_group_form = forms.DoseGroupForm(dose_group)
                if dose_group_form.is_valid():
                    dose_group_form.save()
                else:
                    self.dose_groups_errors = form_error_list_to_ul(dose_group_form)
                    self.object.delete()
                    return self.form_invalid(form)
        else:
            return self.form_invalid(form)

        self.send_message()  # replicate MessageMixin
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context["crud"] = self.crud
        context["animal_group"] = self.animal_group
        context["assessment"] = self.assessment
        context["dose_types"] = models.DoseUnits.json_all()
        if self.request.method == 'POST':  # send back dose-group errors
            context['dose_groups_json'] = self.request.POST['dose_groups_json']
            if hasattr(self, 'dose_groups_errors'):
                context['dose_groups_errors'] = self.dose_groups_errors
        return context


class DosingRegimeRead(BaseDetail):
    model = models.DosingRegime


class DosingRegimeUpdate(AssessmentPermissionsMixin, MessageMixin, UpdateView):
    """
    Update selected dosing regime. Has custom logic to also add dose-groups with
    each creation of a dose-regime.
    """
    model = models.DosingRegime
    form_class = forms.DosingRegimeForm
    success_message = "Dosing regime updated."
    crud = "Update"

    def post(self, request, *args, **kwargs):
        """
        First check if original model is valid. If so, then add to list of valid models.
        Next, go through each dose-group, binding with instance if one exists.
        Make sure each is valid, adding valid to list. Then, if all are valid,
        save each in list. Delete any dose-groups greater than the list.
        """
        valid_forms = []
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            valid_forms.append(form)
            #now, try to save each dose-group
            dose_groups = json.loads(request.POST['dose_groups_json'])

            try:
                models.DoseGroup.clean_formset(dose_groups, self.object.num_dose_groups)
            except ValidationError as e:
                self.dose_groups_errors = e.messages[0]
                return self.form_invalid(form)

            for dose_group in dose_groups:  # todo: make sure ascending order
                try:
                    dose_group_form = forms.DoseGroupForm(dose_group,
                        instance=models.DoseGroup.objects.get(dose_regime=self.object,
                            dose_units=dose_group['dose_units'],
                            dose_group_id=dose_group['dose_group_id']))
                except:
                    dose_group_form = forms.DoseGroupForm(dose_group)
                    dose_group_form.instance.dose_regime = self.object

                if dose_group_form.is_valid():
                    valid_forms.append(dose_group_form)
                else:
                    self.dose_groups_errors = form_error_list_to_ul(dose_group_form)
                    return self.form_invalid(form)
        else:
            return self.form_invalid(form)

        #now, save each form, and delete any existing dose groups not in this set
        for form in valid_forms:
            form.save()
        pks = [form.instance.pk for form in valid_forms]
        models.DoseGroup.objects.filter(dose_regime=self.object.pk)\
                                .exclude(pk__in=pks).delete()

        self.send_message()  # replicate MessageMixin
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context["crud"] = self.crud
        context["assessment"] = context["object"].get_assessment()
        context["dose_types"] = models.DoseUnits.json_all()
        if self.request.method == 'POST':  # send back dose-group errors
            if hasattr(self, 'dose_groups_errors'):
                context['dose_groups_errors'] = self.dose_groups_errors
        return context


class DosingRegimeDelete(BaseDelete):
    success_message = "Dosing regime deleted."
    model = models.DosingRegime

    def get_success_url(self):
        return self.object.dosed_animals.get_absolute_url()


# Endpoint Views
class EndpointCreate(BaseCreate):
    success_message = 'Endpoint created.'
    parent_model = models.AnimalGroup
    parent_template_name = 'animal_group'
    model = models.Endpoint
    form_class = forms.EndpointForm

    def post(self, request, *args, **kwargs):
        #first, try to save endpoint
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            endpoint_model = form.save(commit=False)
            endpoint_model.animal_group = self.parent
            endpoint_model.save()
            form.save_m2m()
            self.object = endpoint_model
            #now, try to save each endpoint group
            egs = json.loads(request.POST['egs_json'])
            for i, eg in enumerate(egs):
                eg['endpoint'] = endpoint_model.pk
                eg_form = forms.EndpointGroupForm(eg)
                if eg_form.is_valid():
                    eg_form.save()
                else:
                    self.egs_errors = form_error_list_to_ul(eg_form)
                    self.object.delete()
                    return self.form_invalid(form)
        else:
            return self.form_invalid(form)

        self.send_message()  # replicate MessageMixin
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(EndpointCreate, self).get_context_data(**kwargs)
        if self.request.method == 'POST':  # send back errors and previous representation
            context['endpoint_json'] = self.request.POST['endpoint_json']
            if hasattr(self, 'egs_errors'):
                context['egs_errors'] = self.egs_errors
        return context


class EndpointUpdate(BaseUpdate):
    success_message = 'Endpoint updated.'
    model = models.Endpoint
    form_class = forms.EndpointForm

    def post(self, request, *args, **kwargs):
        """
        First check if original model is valid. If so, then add to list of valid models.
        Next, go through each EG, binding with instance if one exists. Go through
        each and make sure each is valid, and if so, add to list. Then, if all
        are valid, save each in list. Delete any EGs which greater than the list.
        """
        valid_forms = []
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            valid_forms.append(form)
            #now, try to save each endpoint
            egs = json.loads(request.POST['egs_json'])
            for i, eg in enumerate(egs):
                eg['endpoint'] = self.object.pk
                try:
                    eg_form = forms.EndpointGroupForm(eg,
                        instance=models.EndpointGroup.objects.get(endpoint=self.object.pk, dose_group_id=i))
                except:
                    eg_form = forms.EndpointGroupForm(eg)
                if eg_form.is_valid():
                    valid_forms.append(eg_form)
                else:
                    self.egs_errors = form_error_list_to_ul(eg_form)
                    return self.form_invalid(form)
        else:
            return self.form_invalid(form)

        #now, save each form, and delete any existing dose groups greater than max
        for form in valid_forms:
            form.save()
        models.EndpointGroup.objects.filter(endpoint=self.object.pk,
                                            dose_group_id__gt=len(egs)-1).delete()

        self.send_message()  # replicate MessageMixin
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(EndpointUpdate, self).get_context_data(**kwargs)
        context['animal_group'] = self.object.animal_group
        if self.request.method == 'POST':  # send back errors and previous representation
            context['endpoint_json'] = self.request.POST['endpoint_json']
            if hasattr(self, 'egs_errors'):
                context['egs_errors'] = self.egs_errors
        return context


class EndpointAssessmentList(BaseList):
    # List of Endpoints associated with assessment
    parent_model = Assessment
    model = models.Endpoint
    template_name = "animal/endpoint_list_assessment.html"
    paginate_by = 25

    def get_queryset(self):
        return self.model.objects.filter(assessment=self.assessment)\
                   .select_related('animal_group', 'animal_group__dosing_regime')\
                   .prefetch_related('animal_group__dosing_regime__doses')\
                   .order_by('name')


class EndpointTags(EndpointAssessmentList):
    # List of Endpoints associated with an assessment and tag

    def get_queryset(self):
        return self.model.objects.filter(effects__slug=self.kwargs['tag_slug'])\
                         .select_related('animal_group', 'animal_group__dosing_regime')\
                         .prefetch_related('animal_group__dosing_regime__doses')\
                         .filter(animal_group__in=models.AnimalGroup.objects.filter(
                                    experiment__in=models.Experiment.objects.filter(
                                        study__in=Study.objects.filter(assessment=self.assessment.pk))))


class EndpointSearch(AssessmentPermissionsMixin, FormView):
    """
    Animal endpoint search form.
    """
    crud = 'Read'
    template_name = "animal/endpoint_search.html"
    form_class = forms.EndpointSearchForm

    def dispatch(self, *args, **kwargs):
        self.assessment = get_object_or_404(Assessment, pk=kwargs['pk'])
        self.permission_check_user_can_view()
        return super(EndpointSearch, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EndpointSearch, self).get_context_data(**kwargs)
        context['assessment'] = self.assessment
        return context

    def form_valid(self, form):
        endpoint_dicts = form.search(self.assessment)
        context = self.get_context_data()
        context['endpoints'] = endpoint_dicts
        context['search_terms_div'] = form.get_search_results_div()
        return self.render_to_response(context)


class EndpointRead(BaseDetail):
    queryset = models.Endpoint.objects.select_related('animal_group',
                                                      'animal_group__dosing_regime',
                                                      'animal_group__dosing_regime__experiment',
                                                      'animal_group__dosing_regime__experiment__study')

    def get_context_data(self, **kwargs):
        context = super(EndpointRead, self).get_context_data(**kwargs)
        context['comment_object_type'] = "endpoint"
        context['comment_object_id'] = self.object.pk
        return context


class EndpointReadJSON(BaseDetail):
    model = models.Endpoint

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return HttpResponse(self.object.d_response(), content_type="application/json")


class EndpointDRplot(EndpointRead):
    """Dose-response plot for endpoint only"""
    template_name = "animal/endpoint_dr.html"


class EndpointTDRplot(TemplateView):
    template_name = "animal/endpoint_tdr.html"


class ReviewPlot(TemplateView):
    template_name = "animal/review_plot.html"


class EndpointDelete(BaseDelete):
    success_message = 'Endpoint deleted.'
    model = models.Endpoint

    def get_success_url(self):
        return self.object.animal_group.get_absolute_url()


class EndpointReport(EndpointRead):

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        report = HAWCdocx()
        self.object.docx_print(report, heading_level=1)
        return report.django_response()


class EndpointsReport(BaseList):
    # Word report export for all animal bioassay data in an assessment
    parent_model = Assessment
    model = models.Endpoint

    def get_queryset(self):
        return self.model.objects.filter(assessment=self.assessment)

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        docx = self.model.endpoints_word_report(self.object_list)
        return docx.django_response()


class EndpointFlatFile(BaseList):
    """
    Endpoint flat-file generator.
    Returns a JSON flat-file object of a collection of endpoints.
    """
    parent_model = Assessment
    model = models.Endpoint

    def get_queryset(self, dose=None):
        kwargs = {"assessment": self.assessment}
        if dose:
            kwargs["animal_group__dosing_regime__doses__dose_units"] = dose.pk
        return self.model.objects.filter(**kwargs).distinct('pk')

    def get(self, request, *args, **kwargs):
        output_format = request.GET.get('output', None)

        # get Dose object if one exists, else get None
        dose_pk = self.request.GET.get('dose_pk', -1)
        dose = models.DoseUnits.objects.filter(pk=dose_pk).first()

        self.object_list = self.get_queryset(dose)
        output = self.model.get_flat_file(self.object_list, output_format, dose)
        if output_format == 'tsv':
            content_type = 'text/tab-separated-values'
            disposition = 'attachment; filename="download.tsv"'
        else:
            content_type = 'application/vnd.ms-excel'
            disposition = 'attachment; filename="download.xls"'

        response = HttpResponse(output, content_type=content_type)
        response['Content-Disposition'] = disposition
        return response


class EndpointCrossview(BaseList):
    """
    Endpoint meta-data viewer.
    Returns a JSON flat-file object of a collection of endpoints.
    """
    parent_model = Assessment
    model = models.Endpoint
    template_name = "animal/endpoint_crossview.html"

    def get_queryset(self):
        if self.request.GET.get('dose_pk'):
            self.dose_units = get_object_or_404(models.DoseUnits, pk=self.request.GET['dose_pk'])
        else:
            self.dose_units = models.DoseUnits.objects.get(units='mg/kg-day')
        return self.model.objects.filter(assessment=self.assessment)\
                   .select_related('animal_group', 'animal_group__dosing_regime')\
                   .prefetch_related('animal_group__dosing_regime__doses')\
                   .filter(animal_group__dosing_regime__doses__dose_units=self.dose_units).distinct('pk')


    def get_context_data(self, **kwargs):
        context = super(EndpointCrossview, self).get_context_data(**kwargs)
        context['doses'] = models.DoseUnits.objects.all()
        context['endpoints_json'] = models.Endpoint.d_responses(context['object_list'], self.dose_units.pk)
        return context


# Individual animal view
class EndpointIndividualAnimalCreate(EndpointCreate):
    # Create Endpoint with individual animal data
    template_name = "animal/endpoint_iad_form.html"

    def post(self, request, *args, **kwargs):
        #first, try to save endpoint
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            endpoint_model = form.save(commit=False)
            endpoint_model.individual_animal_data = True
            endpoint_model.animal_group = self.parent
            endpoint_model.save()
            form.save_m2m()
            self.object = endpoint_model
            #now, try to save each endpoint-group
            egs = json.loads(request.POST['egs_json'])
            iads = json.loads(request.POST['iad_json'])
            for i, eg in enumerate(egs):
                eg['endpoint'] = endpoint_model.pk
                eg_form = forms.EndpointGroupForm(eg)
                if eg_form.is_valid():
                    eg_form.save()
                    iads_for_eg = [v for v in iads if v['dose_group_id'] == eg_form.instance.dose_group_id]
                    for iad in iads_for_eg:
                        iad['endpoint_group'] = eg_form.instance.pk
                        iad_form = forms.IndividualAnimalForm(iad)
                        if iad_form.is_valid():
                            iad_form.save()
                        else:
                            self.iad_errors = form_error_list_to_ul(iad_form)
                            self.object.delete()
                            return self.form_invalid(form)
                else:
                    self.egs_errors = form_error_list_to_ul(eg_form)
                    self.object.delete()
                    return self.form_invalid(form)
        else:
            return self.form_invalid(form)

        self.send_message()  # replicate MessageMixin
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(EndpointIndividualAnimalCreate, self).get_context_data(**kwargs)
        if self.request.method == 'POST':  # send back errors and previous representation
            if hasattr(self, 'iad_errors'):
                context['iad_errors'] = self.iad_errors
        return context


class EndpointIndividualAnimalUpdate(EndpointUpdate):
    template_name = "animal/endpoint_iad_form.html"

    def post(self, request, *args, **kwargs):
        """
        First check if original model is valid. If so, then add to list of valid models.
        Next, go through each EG, binding with instance if one exists. Go through
        each and make sure each is valid, and if so, add to list. Then, if all
        are valid, save each in list. Delete any EGs which greater than the list.
        """
        valid_endpoint_forms = []
        valid_iad_forms = []
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            #now, try to save each endpoint
            egs = json.loads(request.POST['egs_json'])
            iads = json.loads(request.POST['iad_json'])
            for i, eg in enumerate(egs):
                eg['endpoint'] = self.object.pk
                try:
                    eg_form = forms.EndpointGroupForm(eg,
                        instance=models.EndpointGroup.objects.get(endpoint=self.object.pk, dose_group_id=i))
                except:
                    eg_form = forms.EndpointGroupForm(eg)
                if eg_form.is_valid():
                    valid_endpoint_forms.append(eg_form)
                    #check individual animal groups
                    iads_for_eg = [v for v in iads if v['dose_group_id'] == eg_form.instance.dose_group_id]
                    for iad in iads_for_eg:
                        iad['endpoint_group'] = eg_form.instance.pk
                        iad_form = forms.IndividualAnimalForm(iad)
                        if iad_form.is_valid():
                            valid_iad_forms.append(iad_form)
                        else:
                            self.iad_errors = form_error_list_to_ul(iad_form)
                            return self.form_invalid(form)
                else:
                    self.egs_errors = form_error_list_to_ul(eg_form)
                    return self.form_invalid(form)
        else:
            return self.form_invalid(form)

        #now, save each form, and delete any existing fields not found here
        form.save()

        valid_eg_pks = []
        for form in valid_endpoint_forms:
            valid_eg = form.save()
            valid_eg_pks.append(valid_eg.pk)
        models.EndpointGroup.objects\
                .filter(endpoint=self.object.pk)\
                .exclude(pk__in=valid_eg_pks).delete()

        valid_iad_models = []
        for form in valid_iad_forms:
            valid_iad_models.append(form.save(commit=False))

        # NOTE that this doesn't update existing objects, but creates entirely new
        # ones. If update is required for auditing-logs, will need to pass the pk
        # for each group-back and forth from model. TODO in future?
        models.IndividualAnimal.objects.filter(endpoint_group__in=valid_eg_pks).delete()
        models.IndividualAnimal.objects.bulk_create(valid_iad_models)

        self.send_message()  # replicate MessageMixin
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(EndpointIndividualAnimalUpdate, self).get_context_data(**kwargs)
        if self.request.method == 'POST':  # send back errors and previous representation
            if hasattr(self, 'iad_errors'):
                context['iad_errors'] = self.iad_errors
        return context


# Uncertainty Factor Endpoint Views
class UFCreate(BaseCreate):
    success_message = 'Uncertainty factor created.'
    parent_model = models.Endpoint
    parent_template_name = 'endpoint'
    model = models.UncertaintyFactorEndpoint
    form_class = forms.UncertaintyFactorEndpointForm

    def get_success_url(self):
        return reverse_lazy('animal:ufs_list', kwargs={'pk': self.object.endpoint.pk})


class UFList(BaseList):
    parent_model = models.Endpoint
    parent_template_name = 'endpoint'
    model = models.UncertaintyFactorEndpoint

    def get_queryset(self):
        return self.model.objects.filter(endpoint=self.parent.pk).order_by('-value')


class UFEdit(BaseUpdate):
    success_message = 'Uncertainty factor updated.'
    model = models.UncertaintyFactorEndpoint
    form_class = forms.UncertaintyFactorEndpointForm

    def get_success_url(self):
        return reverse_lazy('animal:ufs_list', kwargs={'pk': self.object.endpoint.pk})


class UFDelete(BaseDelete):
    success_message = 'Uncertainty Factor deleted.'
    model = models.UncertaintyFactorEndpoint

    def get_success_url(self):
        return reverse_lazy('animal:ufs_list', kwargs={'pk': self.object.endpoint.pk})


class UFRead(BaseDetail):
    model = models.UncertaintyFactorEndpoint


# Aggregation Views
class AggregationCreate(BaseCreate):
    success_message = 'Aggregation created.'
    parent_model = Assessment
    parent_template_name = 'assessment'
    model = models.Aggregation
    form_class = forms.AggregationForm


class AggregationRead(BaseDetail):
    model = models.Aggregation

    def get_context_data(self, **kwargs):
        context = super(AggregationRead, self).get_context_data(**kwargs)
        context['comment_object_type'] = "aggregation"
        context['comment_object_id'] = self.object.pk
        return context


class AggregationReadJSON(AggregationRead):

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return HttpResponse(self.object.get_json(), content_type="application/json")


class AggregationUpdate(BaseUpdate):
    success_message = 'Aggregation updated.'
    model = models.Aggregation
    form_class = forms.AggregationForm


class AggregationDelete(BaseDelete):
    success_message = 'Aggregation deleted.'
    model = models.Aggregation

    def get_success_url(self):
        return reverse_lazy('animal:aggregation_list', kwargs={'pk': self.assessment.pk})


class AggregationAssessmentList(BaseList):
    parent_model = Assessment
    model = models.Aggregation

    def get_queryset(self):
        return self.model.objects.filter(assessment=self.assessment)


class AggregationVersions(BaseVersion):
    model = models.Aggregation
    template_name = "animal/aggregation_versions.html"


class AggregationEndpointFilter(BaseList):
    # Return JSON list of endpoints which meet the dose criteria. Used in
    # aggregation create/update view to select viable endpoints
    parent_model = Assessment
    model = models.Endpoint

    def get_queryset(self):
        self.units = models.DoseUnits.objects.filter(pk=self.request.GET.get('dose_units')).first()
        return models.Endpoint.objects.filter(assessment=self.assessment)

    def get_context_data(self, **kwargs):
        context = []
        if self.units is not None:
            for endpoint in self.object_list:
                doses = endpoint.get_doses_json(json_encode=False)
                for dose in doses:
                    if dose['units_id'] == self.units.pk:
                        context.append({'id': endpoint.pk,
                                        'name': endpoint.get_m2m_representation()})
        return context

    def render_to_response(self, context, **response_kwargs):
        return HttpResponse(json.dumps(context), content_type="application/json")


class AggregationSearch(AssessmentPermissionsMixin, FormView):
    """ Returns JSON representations from aggregation search. POST only."""
    form_class = forms.AggregationSearchForm

    def dispatch(self, *args, **kwargs):
        self.assessment = get_object_or_404(Assessment, pk=kwargs['pk'])
        self.permission_check_user_can_view()
        return super(AggregationSearch, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(FormView, self).get_form_kwargs()
        kwargs['assessment_pk'] = self.assessment.pk
        return kwargs

    def get(self, request, *args, **kwargs):
        raise Http404

    def form_invalid(self, form):
        return HttpResponse(json.dumps({"status": "fail",
                                        "aggregations": [],
                                        "error": "invalid form format"}),
                            content_type="application/json")

    def form_valid(self, form):
        aggregations = form.search()
        return HttpResponse(json.dumps({"status": "success",
                                        "aggregations": aggregations},
                                       cls=HAWCDjangoJSONEncoder),
                            content_type="application/json")


# Uncertainty-Aggregation Views
class UFsAggEdit(BaseUpdate):
    """
    Update view of uncertainty factors for an aggregation. Note that this uses
    the Aggregation model-type for permissions, but POST only edit data related
    to the UncertaintyFactor object.
    """
    success_message = 'Endpoint uncertainty-factors for aggregation updated.'
    model = models.Aggregation
    form_class = forms.AggregationForm
    template_name = "animal/aggregation_ufs_edit.html"

    def get_success_url(self):
        return reverse_lazy('animal:ufs_agg_read', kwargs={'pk': self.object.pk})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        data = json.loads(request.POST['json'])
        for uf in data['ufs']:
            if 'pk' in uf:
                uf_instance = models.UncertaintyFactorEndpoint.objects.get(pk=uf['pk'])
                form = forms.AJAXUncertaintyFactorEndpointForm(uf, instance=uf_instance)
            else:
                form = forms.AJAXUncertaintyFactorEndpointForm(uf, instance=None)
            try:
                form.full_clean()
            except ValidationError:
                pass
            if form.is_valid():
                form.save()
                m = form.save(commit=False)
                m.endpoint = models.Endpoint.objects.get(pk=uf['endpoint'])
                m.save()
        self.send_message()
        return HttpResponseRedirect(self.get_success_url())


class UFsAggRead(AggregationRead):
    # show aggregation with endpoint-level uncertainty factors
    template_name = "animal/aggregation_ufs_read.html"


# Reference-Value Views
class RefValList(BaseList):
    parent_model = Assessment
    model = models.ReferenceValue

    def get_queryset(self):
        return self.model.objects.filter(assessment=self.assessment)


class RefValCreate(BaseCreate):
    success_message = 'Reference value created.'
    parent_model = Assessment
    parent_template_name = 'assessment'
    model = models.ReferenceValue
    form_class = forms.ReferenceValueForm

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save(commit=False)
            self.object.save_meta_information(formset)
            for f in formset:
                uf = f.save(commit=False)
                uf.reference_value = self.object
                uf.save()
            self.send_message()  # replicate MessageMixin
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(RefValCreate, self).get_context_data(**kwargs)

        if self.request.POST:
            context['formset'] = forms.UFRefValFormSet(self.request.POST)
        else:
            # build formset with initial data
            ufs = []
            for choice in models.UncertaintyFactorAbstract.UF_TYPE_CHOICES:
                ufs.append({'uf_type': choice[0]})

            NewRefValFormSet = inlineformset_factory(
                                        models.ReferenceValue,
                                        models.UncertaintyFactorRefVal,
                                        form=forms.UncertaintyFactorRefValForm,
                                        formset=forms.Base_UFRefVal_FormSet,
                                        extra=len(ufs), can_delete=False)
            context['formset'] = NewRefValFormSet(queryset=models.UncertaintyFactorRefVal.objects.none(),
                                                  initial=ufs)

        return context


class RefValRead(BaseDetail):
    model = models.ReferenceValue

    def get_context_data(self, **kwargs):
        context = super(RefValRead, self).get_context_data(**kwargs)
        context['comment_object_type'] = "reference_value"
        context['comment_object_id'] = self.object.pk
        return context


class RefValUpdate(BaseUpdate):
    success_message = 'Reference value updated.'
    model = models.ReferenceValue
    form_class = forms.ReferenceValueForm

    def get_context_data(self, **kwargs):
        context = super(RefValUpdate, self).get_context_data(**kwargs)

        if self.request.POST:
            context['formset'] = forms.UFRefValFormSet(self.request.POST)
        else:
            context['formset'] = forms.UFRefValFormSet(
                                    queryset=models.UncertaintyFactorRefVal.objects.filter(
                                        reference_value=self.object))
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save(commit=False)
            self.object.save_meta_information(formset)
            formset.instance = self.object
            formset.save()
            self.send_message()  # replicate MessageMixin
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))


class RefValDelete(BaseDelete):
    success_message = 'Reference value deleted.'
    model = models.ReferenceValue

    def get_success_url(self):
        return reverse_lazy('animal:ref_val_list', kwargs={'pk': self.assessment.pk})


# Assorted helper functions
class getStrains(TemplateView):
    # Return the valid strains for the requested species in JSON

    def get(self, request, *args, **kwargs):
        strains = []
        try:
            sp = models.Species.objects.get(pk=request.GET.get('species'))
            strains = list(models.Strain.objects.filter(species=sp).values('id', 'name'))
        except:
            pass
        return HttpResponse(json.dumps(strains), content_type="application/json")


class SpeciesCreate(CloseIfSuccessMixin, BaseCreate):
    success_message = 'Species created.'
    parent_model = Assessment
    parent_template_name = 'assessment'
    model = models.Species
    form_class = forms.SpeciesForm


class StrainCreate(CloseIfSuccessMixin, BaseCreate):
    success_message = 'Strain created.'
    parent_model = Assessment
    parent_template_name = 'assessment'
    model = models.Strain
    form_class = forms.StrainForm


class DoseUnitsCreate(CloseIfSuccessMixin, BaseCreate):
    success_message = 'Dose units created.'
    parent_model = Assessment
    parent_template_name = 'assessment'
    model = models.DoseUnits
    form_class = forms.DoseUnitsForm


class FullExport(BaseList):
    """
    Full XLS data export for the animal bioassay data. Does not include any
    aggregation information, uncertainty-values, or reference values.
    """
    parent_model = Assessment
    model = models.Endpoint

    def get_queryset(self):
        return self.model.objects.filter(assessment=self.assessment)

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        xls = models.Endpoint.detailed_excel_export(self.object_list, self.assessment)
        response = HttpResponse(xls, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="download.xls"'
        return response
