import json

from django.db.models import Q
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect

from assessment.models import Assessment, DoseUnits
from lit.models import Reference
from study.models import Study
from study.views import StudyRead
from utils.forms import form_error_list_to_lis, form_error_lis_to_ul
from mgmt.views import EnsureExtractionStartedMixin
from utils.views import (BaseCreate, BaseCreateWithFormset,
                         BaseDelete, BaseDetail,
                         BaseEndpointFilterList, BaseList, BaseUpdate,
                         BaseUpdateWithFormset, MessageMixin,
                         CopyAsNewSelectorMixin)

from . import forms, models, exports


# Experiment Views
class ExperimentCreate(EnsureExtractionStartedMixin, BaseCreate):
    success_message = 'Experiment created.'
    parent_model = Study
    parent_template_name = 'study'
    model = models.Experiment
    form_class = forms.ExperimentForm


class ExperimentRead(BaseDetail):
    model = models.Experiment


class ExperimentCopyAsNewSelector(CopyAsNewSelectorMixin, StudyRead):
    copy_model = models.Experiment
    form_class = forms.ExperimentSelectorForm


class ExperimentUpdate(BaseUpdate):
    success_message = "Experiment updated."
    model = models.Experiment
    form_class = forms.ExperimentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hero_id'] = Study.objects.prefetch_related('identifiers').filter(identifiers__database=2).values_list('identifiers__unique_id', flat=True)
        return context

class ExperimentDelete(BaseDelete):
    success_message = "Experiment deleted."
    model = models.Experiment

    def get_success_url(self):
        return self.object.study.get_absolute_url()


# Animal Group Views
class AnimalGroupCreate(BaseCreate):
    # Create view of AnimalGroup, and sometimes DosingRegime if generational.
    model = models.AnimalGroup
    parent_model = models.Experiment
    template_name = "animal/animalgroup_form.html"
    success_message = "Animal Group created."
    crud = "Create"

    def get_form_class(self):
        self.is_generational = self.parent.is_generational()
        return forms.GenerationalAnimalGroupForm \
            if self.is_generational else forms.AnimalGroupForm

    def form_valid(self, form):
        """
        Save form, and perhaps dosing regime and dosing groups, if appropriate.

        If an animal group is NOT generational, then it requires its own dosing
        regime. Thus, we must make sure the dosing regime is valid before
        attempting to save. If an animal group IS generational, a dosing-regime
        can be specified from parent groups. OR, a dosing-regime can be created.
        """
        self.object = form.save(commit=False)

        # If a dosing-regime is already specified, save as normal
        if self.is_generational and self.object.dosing_regime:
            return super().form_valid(form)

        # Otherwise we create a new dosing-regime, as well as the associated
        # dose-groups using a formset.
        self.form_dosing_regime = forms.DosingRegimeForm(self.request.POST)
        if self.form_dosing_regime.is_valid():
            dosing_regime = self.form_dosing_regime.save(commit=False)

            # unpack dose-groups into formset and validate
            # occasionally POST['dose_groups_json'] will be '', which json.loads
            # will raise an error on. Replace with '{}' on those occasions.
            dose_groups = self.request.POST['dose_groups_json']
            dose_groups_json = dose_groups if dose_groups != '' else '{}'
            fs_initial = json.loads(dose_groups_json)
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

                return super().form_valid(form)

            else:
                # invalid formset; extract formset errors
                lis = []
                for f in fs.forms:
                    if len(list(f.errors.keys())) > 0:
                        lis.extend(form_error_list_to_lis(f))
                if len(fs._non_form_errors) > 0:
                    lis.extend(fs._non_form_errors)
                self.dose_groups_errors = form_error_lis_to_ul(lis)
                return self.form_invalid(form)
        else:
            # invalid dosing-regime
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dose_types"] = DoseUnits.objects.json_all()
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


class AnimalGroupCopyAsNewSelector(CopyAsNewSelectorMixin, ExperimentRead):
    copy_model = models.AnimalGroup
    form_class = forms.AnimalGroupSelectorForm


class AnimalGroupUpdate(BaseUpdate):
    """
    Update selected animal-group. Dosing regime cannot be edited.
    """
    model = models.AnimalGroup
    template_name = "animal/animalgroup_form.html"
    form_class = forms.AnimalGroupForm
    success_message = "Animal Group updated."

    def get_object(self, queryset=None):
        obj = super().get_object()
        self.dosing_regime = obj.dosing_regime
        if obj.is_generational:
            self.form_class = forms.GenerationalAnimalGroupForm
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dose_types"] = DoseUnits.objects.json_all()
        return context


class AnimalGroupDelete(BaseDelete):
    success_message = "Animal-group deleted."
    model = models.AnimalGroup

    def get_success_url(self):
        return self.object.experiment.get_absolute_url()


class EndpointCopyAsNewSelector(CopyAsNewSelectorMixin, AnimalGroupRead):
    copy_model = models.Endpoint
    form_class = forms.EndpointSelectorForm

    def get_related_id(self):
        return self.object.experiment.study_id


# Dosing Regime Views
class DosingRegimeUpdate(BaseUpdate):
    """
    Update selected dosing regime. Has custom logic to also add dose-groups with
    each creation of a dose-regime.
    """
    model = models.DosingRegime
    form_class = forms.DosingRegimeForm
    success_message = "Dosing regime updated."

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
            models.DoseGroup.objects.by_dose_regime(self.object).delete()

            # now save dose-groups, one for each dosing regime
            for dose in fs.forms:
                dose.instance.dose_regime = self.object

            fs.save()

            return super().form_valid(form)

        else:
            # invalid formset; extract formset errors
            lis = []
            for f in fs.forms:
                if len(list(f.errors.keys())) > 0:
                    lis.extend(form_error_list_to_lis(f))
            if len(fs._non_form_errors) > 0:
                lis.extend(fs._non_form_errors)
            self.dose_groups_errors = form_error_lis_to_ul(lis)
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dose_types"] = DoseUnits.objects.json_all()

        if self.request.method == 'POST':  # send back dose-group errors
            context['dose_groups_json'] = self.request.POST['dose_groups_json']
            if hasattr(self, 'dose_groups_errors'):
                context['dose_groups_errors'] = self.dose_groups_errors
        else:
            context["dose_groups_json"] = json.dumps(
                list(self.object.doses.values('dose', 'dose_group_id', 'dose_units')))

        return context

    def get_success_url(self):
        super().get_success_url()
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
        kwargs = super().get_form_kwargs()
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
        context = super().get_context_data(**kwargs)
        context['animal_group'] = self.object.animal_group
        return context


class EndpointList(BaseEndpointFilterList):
    # List of Endpoints associated with assessment
    parent_model = Assessment
    model = models.Endpoint
    form_class = forms.EndpointFilterForm

    def get_query(self, perms):
        query = Q(assessment=self.assessment)
        if not perms['edit']:
            query &= Q(animal_group__experiment__study__published=True)
        return query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dose_units'] = self.form.get_dose_units_id()
        return context


class EndpointTags(EndpointList):
    # List of Endpoints associated with an assessment and tag

    def get_queryset(self):
        return self.model.objects.tag_qs(self.assessment.pk, self.kwargs['tag_slug'])


class EndpointRead(BaseDetail):
    queryset = models.Endpoint.objects\
        .select_related('animal_group',
                        'animal_group__dosing_regime',
                        'animal_group__experiment',
                        'animal_group__experiment__study')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bmd_session'] = self.object.get_latest_bmd_session()
        return context


class EndpointDelete(BaseDelete):
    success_message = 'Endpoint deleted.'
    model = models.Endpoint

    def get_success_url(self):
        return self.object.animal_group.get_absolute_url()


class FullExport(BaseList):
    """
    Full XLS data export for the animal bioassay data.
    """
    parent_model = Assessment
    model = models.Endpoint

    def get_queryset(self):
        perms = self.get_obj_perms()
        if not perms['edit']:
            return self.model.objects.published(self.assessment)
        return self.model.objects.get_qs(self.assessment)

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        exporter = exports.EndpointGroupFlatComplete(
            self.object_list,
            export_format="excel",
            filename='{}-animal-bioassay'.format(self.assessment),
            sheet_name='bioassay-analysis',
            assessment=self.assessment)
        return exporter.build_response()


class EndpointExport(FullExport):
    """
    Compressed summary for viewing endpoint-level information.
    """
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        exporter = exports.EndpointSummary(
            self.object_list,
            export_format="excel",
            filename='{}-animal-bioassay'.format(self.assessment),
            sheet_name='endpoint-summary',
            assessment=self.assessment)
        return exporter.build_response()
