import json

from django.db.models import Q
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.views.generic.edit import CreateView, UpdateView

from assessment.models import Assessment, DoseUnits
from study.models import Study
from utils.forms import form_error_list_to_lis, form_error_lis_to_ul
from utils.views import (MessageMixin, CanCreateMixin,
                         AssessmentPermissionsMixin, CloseIfSuccessMixin,
                         BaseCreate, BaseDelete, BaseDetail, BaseUpdate, BaseList,
                         BaseVersion, GenerateReport, GenerateFixedReport,
                         BaseCreateWithFormset, BaseUpdateWithFormset)

from . import forms, models, exports, reports


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
        self.is_generational = self.experiment.is_generational()
        if self.is_generational:
            self.form_class = forms.GenerationalAnimalGroupForm
        self.assessment = self.experiment.get_assessment()
        return super(AnimalGroupCreate, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CreateView, self).get_form_kwargs()
        kwargs['parent'] = self.experiment
        return kwargs

    def form_valid(self, form):
        """
        If an animal group is NOT generational, then it requires its own dosing
        regime. Thus, we must make sure the dosing regime is valid before
        attempting to save. If an animal group IS generational, a dosing-regime
        can be specified from parent groups. OR, a dosing-regime can be created.
        """
        self.object = form.save(commit=False)

        # If a dosing-regime is already specified, save as normal
        if self.is_generational and self.object.dosing_regime:
            return super(AnimalGroupCreate, self).form_valid(form)

        # Otherwise we create a new dosing-regime, as well as the associated
        # dose-groups using a formset.
        self.form_dosing_regime = forms.DosingRegimeForm(self.request.POST)
        if self.form_dosing_regime.is_valid():
            dosing_regime = self.form_dosing_regime.save(commit=False)

            # unpack dose-groups into formset and validate
            fs_initial = json.loads(self.request.POST['dose_groups_json'])
            fs = forms.dosegroup_formset_factory(fs_initial, dosing_regime.num_dose_groups)

            if fs.is_valid():
                # save dosing-regime and associate animal-group,
                # setting foreign-key interrelationships
                dosing_regime.save()
                self.object.dosing_regime = dosing_regime
                self.object.save()
                dosing_regime.dosed_animals = self.object
                dosing_regime.save()

                # now save dose-groups, one for each dosing regime
                for dose in fs.forms:
                    dose.instance.dose_regime = dosing_regime

                fs.save()

                return super(AnimalGroupCreate, self).form_valid(form)

            else:
                # invalid formset; extract formset errors
                lis = []
                for f in fs.forms:
                    if len(f.errors.keys()) > 0:
                        lis.extend(form_error_list_to_lis(f))
                if len(fs._non_form_errors) > 0:
                    lis.extend(fs._non_form_errors)
                self.dose_groups_errors = form_error_lis_to_ul(lis)
                return self.form_invalid(form)
        else:
            # invalid dosing-regime
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context["crud"] = self.crud
        context["experiment"] = self.experiment
        context["assessment"] = self.assessment
        context["dose_types"] = DoseUnits.json_all()

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
    Update selected animal-group. Dosing regime cannot be edited.
    """
    model = models.AnimalGroup
    template_name = "animal/animalgroup_form.html"
    form_class = forms.AnimalGroupForm
    success_message = "Animal Group updated."
    crud = "Update"

    def get_object(self, queryset=None):
        obj = super(AnimalGroupUpdate, self).get_object()
        self.dosing_regime = obj.dosing_regime
        if obj.is_generational:
            self.form_class = forms.GenerationalAnimalGroupForm
        return obj

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context["crud"] = self.crud
        context["assessment"] = context["object"].get_assessment()
        context["dose_types"] = DoseUnits.json_all()
        return context


class AnimalGroupDelete(BaseDelete):
    success_message = "Animal-group deleted."
    model = models.AnimalGroup

    def get_success_url(self):
        return self.object.experiment.get_absolute_url()


class EndpointCopyAsNewSelector(AnimalGroupRead):
    # Select an existing assessed outcome as a template for a new one
    template_name = 'animal/endpoint_copy_selector.html'

    def get_context_data(self, **kwargs):
        context = super(EndpointCopyAsNewSelector, self).get_context_data(**kwargs)
        context['form'] = forms.EndpointSelectorForm(study_id=self.object.experiment.study_id)
        return context


# Dosing Regime Views
class DosingRegimeUpdate(AssessmentPermissionsMixin, MessageMixin, UpdateView):
    """
    Update selected dosing regime. Has custom logic to also add dose-groups with
    each creation of a dose-regime.
    """
    model = models.DosingRegime
    form_class = forms.DosingRegimeForm
    success_message = "Dosing regime updated."
    crud = "Update"

    def form_valid(self, form):
        """
        If the dosing-regime is valid, then check if the formset is valid. If
        it is, then continue saving.
        """
        self.object = form.save(commit=False)

        # unpack dose-groups into formset and validate
        fs_initial = json.loads(self.request.POST['dose_groups_json'])
        fs = forms.dosegroup_formset_factory(fs_initial, self.object.num_dose_groups)

        if fs.is_valid():
            self.object.save()

            # instead of checking existing vs. new, just delete all old
            # dose-groups, and save new formset
            models.DoseGroup.objects.filter(dose_regime=self.object).delete()

            # now save dose-groups, one for each dosing regime
            for dose in fs.forms:
                dose.instance.dose_regime = self.object

            fs.save()

            return super(DosingRegimeUpdate, self).form_valid(form)

        else:
            # invalid formset; extract formset errors
            lis = []
            for f in fs.forms:
                if len(f.errors.keys()) > 0:
                    lis.extend(form_error_list_to_lis(f))
            if len(fs._non_form_errors) > 0:
                lis.extend(fs._non_form_errors)
            self.dose_groups_errors = form_error_lis_to_ul(lis)
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context["crud"] = self.crud
        context["assessment"] = context["object"].get_assessment()
        context["dose_types"] = DoseUnits.json_all()

        if self.request.method == 'POST':  # send back dose-group errors
            context['dose_groups_json'] = self.request.POST['dose_groups_json']
            if hasattr(self, 'dose_groups_errors'):
                context['dose_groups_errors'] = self.dose_groups_errors
        else:
            context["dose_groups_json"] = json.dumps(
                list(self.object.doses.values('dose', 'dose_group_id', 'dose_units')))

        return context

    def get_success_url(self):
        return self.object.dosed_animals.get_absolute_url()


# Endpoint Views
class EndpointCreate(BaseCreateWithFormset):
    success_message = 'Assessed-outcome created.'
    parent_model = models.AnimalGroup
    parent_template_name = 'animal_group'
    model = models.Endpoint
    form_class = forms.EndpointForm
    formset_factory = forms.EndpointGroupFormSet

    def get_form_kwargs(self):
        kwargs = super(EndpointCreate, self).get_form_kwargs()
        kwargs['assessment'] = self.assessment
        return kwargs

    def build_initial_formset_factory(self):
        Formset = modelformset_factory(
            models.EndpointGroup,
            form=forms.EndpointGroupForm,
            formset=forms.BaseEndpointGroupFormSet,
            extra=self.parent.dosing_regime.num_dose_groups
        )
        return Formset(queryset=models.EndpointGroup.objects.none())

    def pre_validate(self, form, formset):
        # required for dataset-type checks
        for egform in formset.forms:
            egform.endpoint_form = form

    def form_valid(self, form, formset):
        self.object = form.save()
        if self.object.dose_response_available:
            self.post_object_save(form, formset)
            for egform in formset.forms:
                # save all EGs, even if no data
                egform.save()
            self.post_formset_save(form, formset)
        self.send_message()
        return HttpResponseRedirect(self.get_success_url())

    def post_object_save(self, form, formset):
        for i, egform in enumerate(formset.forms):
            egform.instance.endpoint = self.object
            egform.instance.dose_group_id = i


class EndpointUpdate(BaseUpdateWithFormset):
    success_message = 'Endpoint updated.'
    model = models.Endpoint
    form_class = forms.EndpointForm
    formset_factory = forms.EndpointGroupFormSet

    def build_initial_formset_factory(self):
        return forms.EndpointGroupFormSet(queryset=self.object.groups.all())

    def pre_validate(self, form, formset):
        for egform in formset.forms:
            egform.endpoint_form = form

    def form_valid(self, form, formset):
        self.object = form.save()
        self.post_object_save(form, formset)
        for egform in formset.forms:
            # save all EGs, even if no data
            egform.save()
        self.post_formset_save(form, formset)
        self.send_message()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(EndpointUpdate, self).get_context_data(**kwargs)
        context['animal_group'] = self.object.animal_group
        return context


class EndpointList(BaseList):
    # List of Endpoints associated with assessment
    parent_model = Assessment
    model = models.Endpoint

    def get_paginate_by(self, qs):
        val = 25
        try:
            val = int(self.request.GET.get('paginate_by', val))
        except ValueError:
            pass
        return val

    def get(self, request, *args, **kwargs):
        if len(self.request.GET) > 0:
            self.form = forms.EndpointFilterForm(
                self.request.GET,
                assessment_id=self.assessment.id
            )
        else:
            self.form = forms.EndpointFilterForm(
                assessment_id=self.assessment.id
            )
        return super(EndpointList, self).get(request, *args, **kwargs)

    def get_queryset(self):
        perms = super(EndpointList, self).get_obj_perms()

        query = Q(assessment=self.assessment)
        if not perms['edit']:
            query &= Q(animal_group__experiment__study__published=True)
        if self.form.is_valid():
            query &= self.form.get_query()

        return self.model.objects.filter(query).distinct('id')

    def get_context_data(self, **kwargs):
        context = super(EndpointList, self).get_context_data(**kwargs)
        context['form'] = self.form
        context['endpoints_json'] = self.model.d_responses(
            context['object_list'], json_encode=True)
        context['dose_units'] = self.form.get_dose_units_id()
        return context


class EndpointTags(EndpointList):
    # List of Endpoints associated with an assessment and tag

    def get_queryset(self):
        return self.model.objects.filter(effects__slug=self.kwargs['tag_slug'])\
                         .select_related('animal_group', 'animal_group__dosing_regime')\
                         .prefetch_related('animal_group__dosing_regime__doses')\
                         .filter(animal_group__in=models.AnimalGroup.objects.filter(
                                    experiment__in=models.Experiment.objects.filter(
                                        study__in=Study.objects.filter(assessment=self.assessment.pk))))


class EndpointRead(BaseDetail):
    queryset = models.Endpoint.objects\
        .select_related('animal_group',
                        'animal_group__dosing_regime',
                        'animal_group__experiment',
                        'animal_group__experiment__study')

    def get_context_data(self, **kwargs):
        context = super(EndpointRead, self).get_context_data(**kwargs)
        context['comment_object_type'] = "endpoint"
        context['comment_object_id'] = self.object.pk
        return context


class EndpointDelete(BaseDelete):
    success_message = 'Endpoint deleted.'
    model = models.Endpoint

    def get_success_url(self):
        return self.object.animal_group.get_absolute_url()


class EndpointsReport(GenerateReport):
    parent_model = Assessment
    model = models.Endpoint
    report_type = 2

    def get_queryset(self):
        filters = {"assessment": self.assessment}
        perms = super(EndpointsReport, self).get_obj_perms()
        if not perms['edit'] or self.onlyPublished:
            filters["animal_group__experiment__study__published"] = True
        return self.model.objects.filter(**filters)

    def get_filename(self):
        return "animal-bioassay.docx"

    def get_context(self, queryset):
        return self.model.get_docx_template_context(self.assessment, queryset)


class EndpointsFixedReport(GenerateFixedReport):
    parent_model = Assessment
    model = models.Endpoint
    ReportClass = reports.EndpointDOCXReport

    def get_queryset(self):
        filters = {"assessment": self.assessment}
        perms = super(EndpointsFixedReport, self).get_obj_perms()
        if not perms['edit']:
            filters["animal_group__experiment__study__published"] = True
        return self.model.objects.filter(**filters)

    def get_filename(self):
        return "animal-bioassay.docx"

    def get_context(self, queryset):
        return self.model.get_docx_template_context(self.assessment, queryset)


class FullExport(BaseList):
    """
    Full XLS data export for the animal bioassay data.
    """
    parent_model = Assessment
    model = models.Endpoint

    def get_queryset(self):
        filters = {"assessment": self.assessment}
        perms = super(FullExport, self).get_obj_perms()
        if not perms['edit']:
            filters["animal_group__experiment__study__published"] = True
        return self.model.objects.filter(**filters)

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        exporter = exports.EndpointFlatComplete(
                self.object_list,
                export_format="excel",
                filename='{}-animal-bioassay'.format(self.assessment),
                sheet_name='bioassay-analysis',
                assessment=self.assessment)
        return exporter.build_response()
