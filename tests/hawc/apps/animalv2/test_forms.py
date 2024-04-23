from copy import deepcopy

import pytest

from hawc.apps.animalv2 import forms, models
from hawc.apps.assessment import models as assessment_models

# TODO - worth adding more tests here? We could test trying to pass in e.g. a string where the form expects an integer...but the form
# widgets themselves prevent this making it pretty unlikely to encounter in the wild (whereas it's worth testing for in the eventual API).
# for now I've done a few samples and stubbed out the rest, and we can add more if EPA would find it useful.


@pytest.mark.django_db
class TestChemicalForm:
    def test_clean(self):
        instance = models.Chemical.objects.first()

        form = forms.ChemicalForm({}, instance=instance)
        data = deepcopy(form.initial)

        # test success
        form = forms.ChemicalForm(data, instance=instance)
        assert form.is_valid()

        # test `dtxsid`
        data2 = deepcopy(data)
        data2.update(dtxsid="invalid")
        form = forms.ChemicalForm(data2, instance=instance)
        assert form.is_valid() is False
        assert "dtxsid" in form.errors

        valid_dtxsid = assessment_models.DSSTox.objects.first().dtxsid
        data2.update(dtxsid=valid_dtxsid)
        form = forms.ChemicalForm(data2, instance=instance)
        assert form.is_valid() is True


@pytest.mark.django_db
class TestAnimalGroupForm:
    def test_clean(self):
        instance = models.AnimalGroup.objects.first()

        form = forms.AnimalGroupForm({}, instance=instance)
        data = deepcopy(form.initial)

        # test success
        form = forms.AnimalGroupForm(data, instance=instance)
        assert form.is_valid()

        # test `species` / `strain`; what if you give a rat strain with the mouse species?
        rat_species = assessment_models.Species.objects.get(name="rat")
        mouse_species = assessment_models.Species.objects.get(name="mouse")
        rat_strain = assessment_models.Strain.objects.get(species__name="rat")

        data2 = deepcopy(data)
        data2.update(species=mouse_species.id, strain=rat_strain.id)
        form = forms.AnimalGroupForm(data2, instance=instance)
        assert form.is_valid() is False
        assert "strain" in form.errors

        data2.update(species=rat_species.id)
        form = forms.AnimalGroupForm(data2, instance=instance)
        assert form.is_valid() is True


@pytest.mark.django_db
class TestTreatmentForm:
    def test_clean(self):
        instance = models.Treatment.objects.first()

        form = forms.TreatmentForm({}, instance=instance)
        data = deepcopy(form.initial)

        # test success
        form = forms.TreatmentForm(data, instance=instance)
        assert form.is_valid()


@pytest.mark.django_db
class TestEndpointForm:
    def test_clean(self):
        instance = models.Endpoint.objects.first()

        form = forms.EndpointForm({}, instance=instance)
        data = deepcopy(form.initial)

        # test success
        form = forms.EndpointForm(data, instance=instance)
        assert form.is_valid()


@pytest.mark.django_db
class TestObservationTimeForm:
    def test_clean(self):
        instance = models.ObservationTime.objects.first()

        form = forms.ObservationTimeForm({}, instance=instance)
        data = deepcopy(form.initial)

        # test success
        form = forms.ObservationTimeForm(data, instance=instance)
        assert form.is_valid()


@pytest.mark.django_db
class TestDataExtractionForm:
    def test_clean(self):
        instance = models.DataExtraction.objects.first()

        form = forms.DataExtractionForm({}, instance=instance)
        data = deepcopy(form.initial)

        # test success
        form = forms.DataExtractionForm(data, instance=instance)
        assert form.is_valid()
