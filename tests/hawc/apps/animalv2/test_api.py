import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.urls import reverse
from rest_framework.test import APIClient

from hawc.apps.animalv2 import constants, models
from hawc.apps.assessment.models import DoseUnits, EffectTag, Log, Species, Strain
from hawc.apps.study.models import Study


def generic_get_any(model_class):
    return model_class.objects.all().first()


def clone_and_change(d: dict, **kwargs):
    cloned = dict(d)

    for key in kwargs:
        cloned[key] = kwargs[key]

    return cloned


# function that makes a function that checks for an expected count
def generate_browse_checker(count):
    def _browse_test(resp):
        assert resp.json().get("count") == count

    return _browse_test


@pytest.mark.django_db
class TestExperimentViewSet:
    def test_permissions(self, db_keys):
        url = reverse("animalv2:api:experiment-list")
        data = {
            "study": db_keys.study_working,
            "name": "Test Experiment",
            "design": "AA",
            "has_multiple_generations": False,
            "guideline_compliance": "test gl comp",
            "comments": "test comments",
        }
        generic_perm_tester(url, data)

    def test_valid_requests(self, db_keys):
        url = reverse("animalv2:api:experiment-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        data = {
            "study": db_keys.study_working,
            "name": "Test Experiment",
            "design": "AA",
            "has_multiple_generations": False,
            "guideline_compliance": "test gl comp",
            "comments": "test comments",
        }

        just_created_exp_id = None

        def experiment_create_test(resp):
            nonlocal just_created_exp_id

            experiment_id = resp.json()["id"]
            experiment = models.Experiment.objects.get(id=experiment_id)
            assert experiment.comments == data["comments"]

            if just_created_exp_id is None:
                just_created_exp_id = experiment_id

        def altered_experiment_test(resp):
            nonlocal just_created_exp_id

            experiment_id = resp.json()["id"]
            experiment = models.Experiment.objects.get(id=experiment_id)
            assert experiment.comments == "updated"
            assert experiment_id == just_created_exp_id

        def deleted_experiment_test(resp):
            nonlocal just_created_exp_id

            assert resp.data is None

            with pytest.raises(ObjectDoesNotExist):
                models.Experiment.objects.get(id=just_created_exp_id)

        create_scenarios = (
            {
                "desc": "experiment create",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": data,
                "post_request_test": experiment_create_test,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        browse_scenarios = (
            {
                "desc": "experiment browse",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(3),
                "url": f"{url}?assessment_id={db_keys.assessment_working}",
            },
            {
                "desc": "experiment browse on other assessment",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(0),
                "url": f"{url}?assessment_id={db_keys.assessment_client}",
            },
            {
                "desc": "experiment browse with good study filter",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(3),
                "url": f"{url}?assessment_id={db_keys.assessment_working}&study={db_keys.study_working}",
            },
            {
                "desc": "experiment browse with bad study filter",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(0),
                "url": f"{url}?assessment_id={db_keys.assessment_working}&study={db_keys.study_final_bioassay}",
            },
            {
                "desc": "experiment browse without assessment id",
                "expected_code": 400,
                "method": "GET",
                "expected_content": "Please provide an `assessment_id` argument",
                "url": url,
            },
        )
        generic_test_scenarios(client, None, browse_scenarios)

        update_scenarios = (
            {
                "desc": "experiment update",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {"comments": "updated"},
                "method": "PATCH",
                "post_request_test": altered_experiment_test,
            },
        )
        url = f"{url}{just_created_exp_id}/"
        generic_test_scenarios(client, url, update_scenarios)

        read_scenarios = (
            {
                "desc": "experiment read",
                "expected_code": 200,
                "expected_keys": {"id", "study", "comments"},
                "method": "GET",
            },
        )
        generic_test_scenarios(client, url, read_scenarios)

        delete_scenarios = (
            {
                "desc": "experiment delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_experiment_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)

        # test API filtering by study id
        # make a dummy study (so we have something else in the assessment to filter by)
        cloned_study = Study.objects.get(id=db_keys.study_working)
        cloned_study.id = None
        cloned_study.pk = None
        cloned_study.save()

        assert cloned_study.id is not None and cloned_study.id != db_keys.study_working
        url = (
            reverse("animalv2:api:experiment-list") + f"?assessment_id={cloned_study.assessment_id}"
        )

        resp = client.get(url)
        num_experiments_in_assessment = resp.data["count"]

        resp = client.get(url + f"&study={db_keys.study_working}")
        num_experiments_on_study = resp.data["count"]

        resp = client.get(url + f"&study={cloned_study.id}")
        num_experiments_on_other_study = resp.data["count"]

        assert num_experiments_in_assessment == num_experiments_on_study
        assert num_experiments_on_other_study == 0

    def test_bad_requests(self, db_keys):
        url = reverse("animalv2:api:experiment-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        scenarios = (
            {
                "desc": "invalid design",
                "expected_code": 400,
                "expected_keys": {"design"},
                "expected_content": "not a valid choice",
                "data": {"design": "---"},
            },
        )

        generic_test_scenarios(client, url, scenarios)


@pytest.mark.django_db
class TestChemicalViewSet:
    def test_permissions(self, db_keys):
        url = reverse("animalv2:api:chemical-list")
        data = {
            "experiment": db_keys.animalv2_experiment,
            "name": "Test Chemical",
        }

        generic_perm_tester(url, data)

    def test_valid_requests(self, db_keys):
        url = reverse("animalv2:api:chemical-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        data = {
            "experiment": db_keys.animalv2_experiment,
            "name": "Test Chemical",
            "dtxsid_id": "DTXSID7020970",
            "cas": "cas",
            "source": "src",
            "vehicle": "veh",
            "purity": "pur",
            "comments": "comm",
        }

        just_created_chemical_id = None

        def chemical_create_test(resp):
            nonlocal just_created_chemical_id

            chemical_id = resp.json()["id"]
            chemical = models.Chemical.objects.get(id=chemical_id)
            assert chemical.comments == data["comments"]
            assert chemical.dtxsid is not None

            if just_created_chemical_id is None:
                just_created_chemical_id = chemical_id

        def altered_chemical_test(resp):
            nonlocal just_created_chemical_id

            chemical_id = resp.json()["id"]
            chemical = models.Chemical.objects.get(id=chemical_id)
            assert chemical.comments == "updated"
            assert chemical_id == just_created_chemical_id

        def deleted_chemical_test(resp):
            nonlocal just_created_chemical_id

            assert resp.data is None

            with pytest.raises(ObjectDoesNotExist):
                models.Chemical.objects.get(id=just_created_chemical_id)

        create_scenarios = (
            {
                "desc": "chemical create",
                "expected_code": 201,
                "expected_keys": {"id", "dtxsid", "cas", "source"},
                "data": data,
                "post_request_test": chemical_create_test,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        browse_scenarios = (
            {
                "desc": "chemical browse",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(2),
                "url": f"{url}?assessment_id={db_keys.assessment_working}",
            },
            {
                "desc": "chemical browse on other assessment",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(0),
                "url": f"{url}?assessment_id={db_keys.assessment_client}",
            },
            {
                "desc": "chemical browse with good experiment filter",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(2),
                "url": f"{url}?assessment_id={db_keys.assessment_working}&experiment={db_keys.animalv2_experiment}",
            },
            {
                "desc": "chemical browse with bad experiment filter",
                "expected_code": 400,
                "expected_keys": {"experiment"},
                "expected_content": "invalid_choice",
                "method": "GET",
                "url": f"{url}?assessment_id={db_keys.assessment_working}&experiment=777",
            },
            {
                "desc": "chemical browse without assessment id",
                "expected_code": 400,
                "method": "GET",
                "expected_content": "Please provide an `assessment_id` argument",
                "url": url,
            },
        )
        generic_test_scenarios(client, None, browse_scenarios)

        update_scenarios = (
            {
                "desc": "chemical update",
                "expected_code": 200,
                "expected_keys": {"id", "dtxsid", "cas", "source"},
                "data": {"comments": "updated"},
                "method": "PATCH",
                "post_request_test": altered_chemical_test,
            },
        )
        url = f"{url}{just_created_chemical_id}/"
        generic_test_scenarios(client, url, update_scenarios)

        read_scenarios = (
            {
                "desc": "chemical read",
                "expected_code": 200,
                "expected_keys": {"id", "experiment", "comments"},
                "method": "GET",
            },
        )
        generic_test_scenarios(client, url, read_scenarios)

        delete_scenarios = (
            {
                "desc": "chemical delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_chemical_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)

    def test_bad_requests(self, db_keys):
        url = reverse("animalv2:api:chemical-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        scenarios = (
            {
                "desc": "invalid experiment",
                "expected_code": 400,
                "expected_keys": {"experiment"},
                "expected_content": "does not exist",
                "data": {"experiment": 999},
            },
            {
                "desc": "missing name",
                "expected_code": 400,
                "expected_keys": {"name"},
                "expected_content": "required",
                "data": {},
            },
            {
                "desc": "bad dtxsid",
                "expected_code": 400,
                "expected_keys": {"dtxsid_id"},
                "expected_content": "does not exist",
                "data": {
                    "experiment": db_keys.animalv2_experiment,
                    "name": "name",
                    "dtxsid_id": "XXX",
                },
            },
        )

        generic_test_scenarios(client, url, scenarios)


@pytest.mark.django_db
class TestAnimalGroupViewSet:
    def test_permissions(self, db_keys):
        url = reverse("animalv2:api:animal-group-list")
        strain = generic_get_any(Strain)
        data = {
            "experiment": db_keys.animalv2_experiment,
            "name": "Test Animal Group",
            "species_id": strain.species.id,
            "strain_id": strain.id,
            "sex": constants.Sex.MALE,
        }

        generic_perm_tester(url, data)

    def test_valid_requests(self, db_keys):
        url = reverse("animalv2:api:animal-group-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        some_strain = generic_get_any(Strain)
        some_ag = generic_get_any(models.AnimalGroup)

        data = {
            "experiment": db_keys.animalv2_experiment,
            "name": "Test Animal Group",
            "species_id": some_strain.species.id,
            "strain_id": some_strain.id,
            "sex": constants.Sex.MALE,
            "comments": "com",
            "parent_ids": [some_ag.id],
        }

        just_created_animal_group_id = None

        def animal_group_create_test(resp):
            nonlocal just_created_animal_group_id

            animal_group_id = resp.json()["id"]
            animal_group = models.AnimalGroup.objects.get(id=animal_group_id)
            assert animal_group.comments == data["comments"]
            assert animal_group.species is not None
            assert animal_group.sex is not None

            if just_created_animal_group_id is None:
                just_created_animal_group_id = animal_group_id

        def altered_animal_group_test(resp):
            nonlocal just_created_animal_group_id

            animal_group_id = resp.json()["id"]
            animal_group = models.AnimalGroup.objects.get(id=animal_group_id)
            assert animal_group.comments == "updated"
            assert animal_group_id == just_created_animal_group_id

        def deleted_animal_group_test(resp):
            nonlocal just_created_animal_group_id

            assert resp.data is None

            with pytest.raises(ObjectDoesNotExist):
                models.AnimalGroup.objects.get(id=just_created_animal_group_id)

        create_scenarios = (
            {
                "desc": "animal_group create",
                "expected_code": 201,
                "expected_keys": {"id", "species", "strain", "sex"},
                "data": data,
                "post_request_test": animal_group_create_test,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        browse_scenarios = (
            {
                "desc": "animalgroup browse",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(2),
                "url": f"{url}?assessment_id={db_keys.assessment_working}",
            },
            {
                "desc": "animalgroup browse on other assessment",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(0),
                "url": f"{url}?assessment_id={db_keys.assessment_client}",
            },
            {
                "desc": "animalgroup browse with good experiment filter",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(2),
                "url": f"{url}?assessment_id={db_keys.assessment_working}&experiment={db_keys.animalv2_experiment}",
            },
            {
                "desc": "animalgroup browse with bad experiment filter",
                "expected_code": 400,
                "expected_keys": {"experiment"},
                "expected_content": "invalid_choice",
                "method": "GET",
                "url": f"{url}?assessment_id={db_keys.assessment_working}&experiment=777",
            },
            {
                "desc": "animalgroup browse without assessment id",
                "expected_code": 400,
                "method": "GET",
                "expected_content": "Please provide an `assessment_id` argument",
                "url": url,
            },
        )
        generic_test_scenarios(client, None, browse_scenarios)

        update_scenarios = (
            {
                "desc": "animal_group update",
                "expected_code": 200,
                "expected_keys": {"id", "species", "strain", "sex"},
                "data": {"comments": "updated"},
                "method": "PATCH",
                "post_request_test": altered_animal_group_test,
            },
            {
                "desc": "alternate sex",
                "expected_code": 200,
                "expected_keys": {"id", "species", "strain", "sex"},
                "data": {"sex": "Female"},
                "method": "PATCH",
                "post_request_test": altered_animal_group_test,
            },
        )
        url = f"{url}{just_created_animal_group_id}/"
        generic_test_scenarios(client, url, update_scenarios)

        read_scenarios = (
            {
                "desc": "animal_group read",
                "expected_code": 200,
                "expected_keys": {"id", "experiment", "comments"},
                "method": "GET",
            },
        )
        generic_test_scenarios(client, url, read_scenarios)

        delete_scenarios = (
            {
                "desc": "animal_group delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_animal_group_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)

    def test_bad_requests(self, db_keys):
        url = reverse("animalv2:api:animal-group-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        some_strain = generic_get_any(Strain)
        some_other_species = Species.objects.filter(~Q(id=some_strain.species.id)).first()
        some_other_experiment = models.Experiment.objects.filter(
            ~Q(id=db_keys.animalv2_experiment)
        ).first()

        good_data = {
            "experiment": db_keys.animalv2_experiment,
            "name": "Test Animal Group",
            "species_id": some_strain.species.id,
            "strain_id": some_strain.id,
            "sex": constants.Sex.MALE,
            "comments": "com",
        }

        scenarios = (
            {
                "desc": "invalid experiment",
                "expected_code": 400,
                "expected_keys": {"experiment"},
                "expected_content": "does not exist",
                "data": {"experiment": 999},
            },
            {
                "desc": "missing req'd fields",
                "expected_code": 400,
                "expected_keys": {"name", "species_id", "strain_id"},
                "expected_content": "required",
                "data": {},
            },
            {
                "desc": "bad sex",
                "expected_code": 400,
                "expected_keys": {"sex"},
                "expected_content": "is required",
                "data": {"sex": "invalid"},
            },
            {
                "desc": "species/strain mismatch",
                "expected_code": 400,
                "expected_keys": {"strain"},
                "expected_content": "Strain must be valid for species",
                "data": clone_and_change(good_data, species_id=some_other_species.id),
            },
        )
        generic_test_scenarios(client, url, scenarios)

        just_created_animal_group_id = None
        other_animal_group_id = None

        def animal_group_create_test(resp):
            nonlocal just_created_animal_group_id
            just_created_animal_group_id = resp.json()["id"]

        def other_animal_group_create_test(resp):
            nonlocal other_animal_group_id
            other_animal_group_id = resp.json()["id"]

        # make real item(s), we need to test a few other cases
        generic_test_scenario(
            client,
            url,
            {
                "desc": "animal_group create",
                "expected_code": 201,
                "expected_keys": {"id", "species", "strain", "sex"},
                "data": good_data,
                "post_request_test": animal_group_create_test,
            },
        )

        generic_test_scenario(
            client,
            url,
            {
                "desc": "animal_group other create",
                "expected_code": 201,
                "expected_keys": {"id", "species", "strain", "sex"},
                "data": clone_and_change(
                    good_data, name="Other", experiment=some_other_experiment.id
                ),
                "post_request_test": other_animal_group_create_test,
            },
        )

        scenarios = (
            {
                "desc": "circular parent reference",
                "method": "PATCH",
                "expected_code": 400,
                "expected_keys": {"parent_ids"},
                "expected_content": "Self cannot be parent of self",
                "data": clone_and_change(good_data, parent_ids=[just_created_animal_group_id]),
            },
            {
                "desc": "non-experiment animalgroup",
                "method": "PATCH",
                "expected_code": 400,
                "expected_keys": {"parent_ids"},
                "expected_content": "mismatched",
                "data": clone_and_change(good_data, parent_ids=[other_animal_group_id]),
            },
        )
        url = f"{url}{just_created_animal_group_id}/"
        generic_test_scenarios(client, url, scenarios)


@pytest.mark.django_db
class TestTreatmentViewSet:
    def test_permissions(self, db_keys):
        url = reverse("animalv2:api:treatment-list")
        chem = generic_get_any(models.Chemical)
        data = {
            "experiment": db_keys.animalv2_experiment,
            "name": "Test Treatment",
            "chemical_id": chem.id,
            "route_of_exposure": constants.RouteExposure.OR,
        }

        generic_perm_tester(url, data)

    def test_valid_requests(self, db_keys):
        url = reverse("animalv2:api:treatment-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        chem = generic_get_any(models.Chemical)

        data = {
            "experiment": db_keys.animalv2_experiment,
            "name": "Test Treatment",
            "chemical_id": chem.id,
            "route_of_exposure": constants.RouteExposure.OR,
            "exposure_duration": 9.8,
            "exposure_duration_description": "desc",
            "exposure_outcome_duration": 1.9,
            "comments": "comm",
        }

        just_created_treatment_id = None

        def treatment_create_test(resp):
            nonlocal just_created_treatment_id

            treatment_id = resp.json()["id"]
            treatment = models.Treatment.objects.get(id=treatment_id)
            assert treatment.comments == data["comments"]
            assert treatment.chemical is not None

            if just_created_treatment_id is None:
                just_created_treatment_id = treatment_id

        def altered_treatment_test(resp):
            nonlocal just_created_treatment_id

            treatment_id = resp.json()["id"]
            treatment = models.Treatment.objects.get(id=treatment_id)
            assert treatment.comments == "updated"
            assert treatment_id == just_created_treatment_id

        def deleted_treatment_test(resp):
            nonlocal just_created_treatment_id

            assert resp.data is None

            with pytest.raises(ObjectDoesNotExist):
                models.Treatment.objects.get(id=just_created_treatment_id)

        create_scenarios = (
            {
                "desc": "treatment create",
                "expected_code": 201,
                "expected_keys": {"id", "chemical", "route_of_exposure", "comments"},
                "data": data,
                "post_request_test": treatment_create_test,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        browse_scenarios = (
            {
                "desc": "treatment browse",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(2),
                "url": f"{url}?assessment_id={db_keys.assessment_working}",
            },
            {
                "desc": "treatment browse on other assessment",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(0),
                "url": f"{url}?assessment_id={db_keys.assessment_client}",
            },
            {
                "desc": "treatment browse with good experiment filter",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(2),
                "url": f"{url}?assessment_id={db_keys.assessment_working}&experiment={db_keys.animalv2_experiment}",
            },
            {
                "desc": "treatment browse with bad experiment filter",
                "expected_code": 400,
                "expected_keys": {"experiment"},
                "expected_content": "invalid_choice",
                "method": "GET",
                "url": f"{url}?assessment_id={db_keys.assessment_working}&experiment=777",
            },
            {
                "desc": "treatment browse without assessment id",
                "expected_code": 400,
                "method": "GET",
                "expected_content": "Please provide an `assessment_id` argument",
                "url": url,
            },
        )
        generic_test_scenarios(client, None, browse_scenarios)

        update_scenarios = (
            {
                "desc": "treatment update",
                "expected_code": 200,
                "expected_keys": {"id", "chemical", "route_of_exposure", "comments"},
                "data": {"comments": "updated"},
                "method": "PATCH",
                "post_request_test": altered_treatment_test,
            },
            {
                "desc": "alternate route",
                "expected_code": 200,
                "expected_keys": {"id", "chemical", "route_of_exposure", "comments"},
                "data": {"route_of_exposure": "Oral Capsule"},
                "method": "PATCH",
                "post_request_test": altered_treatment_test,
            },
        )
        url = f"{url}{just_created_treatment_id}/"
        generic_test_scenarios(client, url, update_scenarios)

        read_scenarios = (
            {
                "desc": "treatment read",
                "expected_code": 200,
                "expected_keys": {"id", "experiment", "comments"},
                "method": "GET",
            },
        )
        generic_test_scenarios(client, url, read_scenarios)

        delete_scenarios = (
            {
                "desc": "treatment delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_treatment_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)

    def test_bad_requests(self, db_keys):
        url = reverse("animalv2:api:treatment-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        scenarios = (
            {
                "desc": "invalid experiment",
                "expected_code": 400,
                "expected_keys": {"experiment"},
                "expected_content": "does not exist",
                "data": {"experiment": 999},
            },
            {
                "desc": "missing req'd fields",
                "expected_code": 400,
                "expected_keys": {"name", "chemical_id", "route_of_exposure"},
                "expected_content": "required",
                "data": {},
            },
            {
                "desc": "bad route",
                "expected_code": 400,
                "expected_keys": {"route_of_exposure"},
                "expected_content": "is required",
                "data": {"route_of_exposure": "invalid"},
            },
        )
        generic_test_scenarios(client, url, scenarios)


@pytest.mark.django_db
class TestDoseGroupViewSet:
    def test_permissions(self, db_keys):
        url = reverse("animalv2:api:dose-group-list")
        treatment = generic_get_any(models.Treatment)
        dose_units = generic_get_any(DoseUnits)
        data = {
            "treatment": treatment.id,
            "dose_group_id": 1,
            "dose": 1.5,
            "dose_units": dose_units.name,
        }

        generic_perm_tester(url, data)

    def test_valid_requests(self, db_keys):
        url = reverse("animalv2:api:dose-group-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        treatment = generic_get_any(models.Treatment)
        dose_units = generic_get_any(DoseUnits)
        data = {
            "treatment": treatment.id,
            "dose_group_id": 1,
            "dose": 1.5,
            "dose_units": dose_units.name,
        }

        just_created_dg_id = None

        def dg_create_test(resp):
            nonlocal just_created_dg_id

            dg_id = resp.json()["id"]
            dg = models.DoseGroup.objects.get(id=dg_id)
            assert dg.dose == data["dose"]
            assert dg.dose_units is not None

            if just_created_dg_id is None:
                just_created_dg_id = dg_id

        def altered_dg_test(resp):
            nonlocal just_created_dg_id

            dg_id = resp.json()["id"]
            dg = models.DoseGroup.objects.get(id=dg_id)
            assert dg.dose == 4.5
            assert dg_id == just_created_dg_id

        def deleted_dg_test(resp):
            nonlocal just_created_dg_id

            assert resp.data is None

            with pytest.raises(ObjectDoesNotExist):
                models.DoseGroup.objects.get(id=just_created_dg_id)

        create_scenarios = (
            {
                "desc": "dg create",
                "expected_code": 201,
                "expected_keys": {"treatment", "dose_group_id", "dose", "dose_units"},
                "data": data,
                "post_request_test": dg_create_test,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        browse_scenarios = (
            {
                "desc": "dosegroup browse",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(2),
                "url": f"{url}?assessment_id={db_keys.assessment_working}",
            },
            {
                "desc": "dosegroup browse on other assessment",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(0),
                "url": f"{url}?assessment_id={db_keys.assessment_client}",
            },
            {
                "desc": "dosegroup browse with good treatment filter",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(2),
                "url": f"{url}?assessment_id={db_keys.assessment_working}&treatment={treatment.id}",
            },
            {
                "desc": "dosegroup browse with bad treatment filter",
                "expected_code": 400,
                "expected_keys": {"treatment"},
                "expected_content": "invalid_choice",
                "method": "GET",
                "url": f"{url}?assessment_id={db_keys.assessment_working}&treatment=555",
            },
            {
                "desc": "dosegroup browse without assessment id",
                "expected_code": 400,
                "method": "GET",
                "expected_content": "Please provide an `assessment_id` argument",
                "url": url,
            },
        )
        generic_test_scenarios(client, None, browse_scenarios)

        update_scenarios = (
            {
                "desc": "dg update",
                "expected_code": 200,
                "expected_keys": {"treatment", "dose_group_id", "dose", "dose_units"},
                "data": {"dose": 4.5},
                "method": "PATCH",
                "post_request_test": altered_dg_test,
            },
        )
        url = f"{url}{just_created_dg_id}/"
        generic_test_scenarios(client, url, update_scenarios)

        read_scenarios = (
            {
                "desc": "dg read",
                "expected_code": 200,
                "expected_keys": {"treatment", "dose_group_id", "dose", "dose_units"},
                "method": "GET",
            },
        )
        generic_test_scenarios(client, url, read_scenarios)

        delete_scenarios = (
            {
                "desc": "dg delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_dg_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)

    def test_bad_requests(self, db_keys):
        url = reverse("animalv2:api:dose-group-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        scenarios = (
            {
                "desc": "invalid treatment",
                "expected_code": 400,
                "expected_keys": {"treatment"},
                "expected_content": "does not exist",
                "data": {"treatment": 999},
            },
            {
                "desc": "missing req'd fields",
                "expected_code": 400,
                "expected_keys": {"treatment", "dose_group_id", "dose", "dose_units"},
                "expected_content": "required",
                "data": {},
            },
            {
                "desc": "bad dose units",
                "expected_code": 400,
                "expected_keys": {"dose_units"},
                "expected_content": "does not exist",
                "data": {"dose_units": "invalid"},
            },
        )
        generic_test_scenarios(client, url, scenarios)


@pytest.mark.django_db
class TestEndpointViewSet:
    def test_permissions(self, db_keys):
        url = reverse("animalv2:api:endpoint-list")
        data = {
            "experiment": db_keys.animalv2_experiment,
            "name": "Test Endpoint",
        }

        generic_perm_tester(url, data)

    def test_valid_requests(self, db_keys):
        url = reverse("animalv2:api:endpoint-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        tag = generic_get_any(EffectTag)

        data = {
            "experiment": db_keys.animalv2_experiment,
            "name": "Test Endpoint",
            "system": "s",
            "organ": "o",
            "effect": "e",
            "effect_subtype": "st",
            "effect_modifier_timing": "timing",
            "effect_modifier_reference": "ref",
            "effect_modifier_anatomical": "ana",
            "effect_modifier_location": "loc",
            "additional_tags": [tag.slug],
            "comments": "comm",
        }

        just_created_endpoint_id = None

        def endpoint_create_test(resp):
            nonlocal just_created_endpoint_id

            endpoint_id = resp.json()["id"]
            endpoint = models.Endpoint.objects.get(id=endpoint_id)
            assert endpoint.comments == data["comments"]

            if just_created_endpoint_id is None:
                just_created_endpoint_id = endpoint_id

        def altered_endpoint_test(resp):
            nonlocal just_created_endpoint_id

            endpoint_id = resp.json()["id"]
            endpoint = models.Endpoint.objects.get(id=endpoint_id)
            assert endpoint.comments == "updated"
            assert endpoint_id == just_created_endpoint_id

        def deleted_endpoint_test(resp):
            nonlocal just_created_endpoint_id

            assert resp.data is None

            with pytest.raises(ObjectDoesNotExist):
                models.Endpoint.objects.get(id=just_created_endpoint_id)

        create_scenarios = (
            {
                "desc": "endpoint create",
                "expected_code": 201,
                "expected_keys": {"id", "name", "system", "organ", "additional_tags"},
                "data": data,
                "post_request_test": endpoint_create_test,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        browse_scenarios = (
            {
                "desc": "endpoint browse",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(2),
                "url": f"{url}?assessment_id={db_keys.assessment_working}",
            },
            {
                "desc": "endpoint browse on other assessment",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(0),
                "url": f"{url}?assessment_id={db_keys.assessment_client}",
            },
            {
                "desc": "endpoint browse with good experiment filter",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(2),
                "url": f"{url}?assessment_id={db_keys.assessment_working}&experiment={db_keys.animalv2_experiment}",
            },
            {
                "desc": "endpoint browse with bad experiment filter",
                "expected_code": 400,
                "expected_keys": {"experiment"},
                "expected_content": "invalid_choice",
                "method": "GET",
                "url": f"{url}?assessment_id={db_keys.assessment_working}&experiment=777",
            },
            {
                "desc": "endpoint browse without assessment id",
                "expected_code": 400,
                "method": "GET",
                "expected_content": "Please provide an `assessment_id` argument",
                "url": url,
            },
        )
        generic_test_scenarios(client, None, browse_scenarios)

        update_scenarios = (
            {
                "desc": "endpoint update",
                "expected_code": 200,
                "expected_keys": {"id", "name", "system", "organ", "additional_tags"},
                "data": {"comments": "updated"},
                "method": "PATCH",
                "post_request_test": altered_endpoint_test,
            },
        )
        url = f"{url}{just_created_endpoint_id}/"
        generic_test_scenarios(client, url, update_scenarios)

        read_scenarios = (
            {
                "desc": "endpoint read",
                "expected_code": 200,
                "expected_keys": {"id", "experiment", "comments"},
                "method": "GET",
            },
        )
        generic_test_scenarios(client, url, read_scenarios)

        delete_scenarios = (
            {
                "desc": "endpoint delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_endpoint_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)

    def test_bad_requests(self, db_keys):
        url = reverse("animalv2:api:endpoint-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        scenarios = (
            {
                "desc": "invalid experiment",
                "expected_code": 400,
                "expected_keys": {"experiment"},
                "expected_content": "does not exist",
                "data": {"experiment": 999},
            },
            {
                "desc": "bad tag",
                "expected_code": 400,
                "expected_keys": {"additional_tags"},
                "expected_content": "does not exist",
                "data": {"experiment": db_keys.animalv2_experiment, "additional_tags": ["xxx"]},
            },
        )

        generic_test_scenarios(client, url, scenarios)


@pytest.mark.django_db
class TestObservationTimeViewSet:
    def test_permissions(self, db_keys):
        url = reverse("animalv2:api:observation-time-list")
        endpoint = generic_get_any(models.Endpoint)
        data = {
            "endpoint_id": endpoint.id,
            "observation_time": 1,
            "observation_time_units": constants.ObservationTimeUnits.MIN,
        }

        generic_perm_tester(url, data)

    def test_valid_requests(self, db_keys):
        url = reverse("animalv2:api:observation-time-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        endpoint = generic_get_any(models.Endpoint)
        data = {
            "endpoint_id": endpoint.id,
            "observation_time": 1.5,
            "observation_time_units": constants.ObservationTimeUnits.MIN,
        }

        just_created_obstime_id = None

        def obstime_create_test(resp):
            nonlocal just_created_obstime_id

            obstime_id = resp.json()["id"]
            obstime = models.ObservationTime.objects.get(id=obstime_id)
            assert obstime.observation_time == data["observation_time"]
            assert obstime.observation_time_units is not None

            if just_created_obstime_id is None:
                just_created_obstime_id = obstime_id

        def altered_obstime_test(resp):
            nonlocal just_created_obstime_id

            obstime_id = resp.json()["id"]
            obstime = models.ObservationTime.objects.get(id=obstime_id)
            assert obstime.observation_time == 7.43
            assert obstime_id == just_created_obstime_id

        def deleted_obstime_test(resp):
            nonlocal just_created_obstime_id

            assert resp.data is None

            with pytest.raises(ObjectDoesNotExist):
                models.ObservationTime.objects.get(id=just_created_obstime_id)

        create_scenarios = (
            {
                "desc": "obstime create",
                "expected_code": 201,
                "expected_keys": {"endpoint", "observation_time", "observation_time_units"},
                "data": data,
                "post_request_test": obstime_create_test,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        browse_scenarios = (
            {
                "desc": "obstime browse",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(2),
                "url": f"{url}?assessment_id={db_keys.assessment_working}",
            },
            {
                "desc": "obstime browse on other assessment",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(0),
                "url": f"{url}?assessment_id={db_keys.assessment_client}",
            },
            {
                "desc": "obstime browse with good endpoint filter",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(2),
                "url": f"{url}?assessment_id={db_keys.assessment_working}&endpoint={endpoint.id}",
            },
            {
                "desc": "obstime browse with bad endpoint filter",
                "expected_code": 400,
                "expected_keys": {"endpoint"},
                "expected_content": "invalid_choice",
                "method": "GET",
                "url": f"{url}?assessment_id={db_keys.assessment_working}&endpoint=444",
            },
            {
                "desc": "obstime browse without assessment id",
                "expected_code": 400,
                "method": "GET",
                "expected_content": "Please provide an `assessment_id` argument",
                "url": url,
            },
        )
        generic_test_scenarios(client, None, browse_scenarios)

        update_scenarios = (
            {
                "desc": "obstime update",
                "expected_code": 200,
                "expected_keys": {"endpoint", "observation_time", "observation_time_units"},
                "data": {"observation_time": 7.43},
                "method": "PATCH",
                "post_request_test": altered_obstime_test,
            },
        )
        url = f"{url}{just_created_obstime_id}/"
        generic_test_scenarios(client, url, update_scenarios)

        read_scenarios = (
            {
                "desc": "obstime read",
                "expected_code": 200,
                "expected_keys": {"endpoint", "observation_time", "observation_time_units"},
                "method": "GET",
            },
        )
        generic_test_scenarios(client, url, read_scenarios)

        delete_scenarios = (
            {
                "desc": "obstime delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_obstime_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)

    def test_bad_requests(self, db_keys):
        url = reverse("animalv2:api:observation-time-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        scenarios = (
            {
                "desc": "invalid endpoint",
                "expected_code": 400,
                "expected_keys": {"endpoint_id"},
                "expected_content": "does not exist",
                "data": {"endpoint_id": 999},
            },
            {
                "desc": "missing req'd fields",
                "expected_code": 400,
                "expected_keys": {"endpoint_id", "observation_time_units"},
                "expected_content": "required",
                "data": {},
            },
            {
                "desc": "bad observation time units",
                "expected_code": 400,
                "expected_keys": {"observation_time_units"},
                "expected_content": "not a valid choice",
                "data": {"observation_time_units": "invalid"},
            },
        )
        generic_test_scenarios(client, url, scenarios)


@pytest.mark.django_db
class TestDataExtractionViewSet:
    def test_permissions(self, db_keys):
        url = reverse("animalv2:api:data-extraction-list")
        endpoint = generic_get_any(models.Endpoint)
        treatment = generic_get_any(models.Treatment)
        obstime = generic_get_any(models.ObservationTime)
        data = {
            "experiment": db_keys.animalv2_experiment,
            "endpoint": endpoint.id,
            "treatment": treatment.id,
            "observation_timepoint": obstime.id,
            "result_details": "test details",
            "dose_response_observations": "test observations",
            "method_to_control_for_litter_effects": constants.MethodToControlForLitterEffects.YES,
            "dataset_type": constants.DatasetType.NOT_REPORTED,
        }

        generic_perm_tester(url, data)

    def test_valid_requests(self, db_keys):
        url = reverse("animalv2:api:data-extraction-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        endpoint = generic_get_any(models.Endpoint)
        treatment = generic_get_any(models.Treatment)
        obstime = generic_get_any(models.ObservationTime)

        data = {
            "experiment": db_keys.animalv2_experiment,
            "endpoint": endpoint.id,
            "treatment": treatment.id,
            "observation_timepoint": obstime.id,
            "result_details": "test details",
            "dose_response_observations": "test observations",
            "method_to_control_for_litter_effects": constants.MethodToControlForLitterEffects.YES,
            "dataset_type": constants.DatasetType.NOT_REPORTED,
        }

        just_created_de_id = None

        def de_create_test(resp):
            nonlocal just_created_de_id

            de_id = resp.json()["id"]
            de = models.DataExtraction.objects.get(id=de_id)
            assert de.dose_response_observations == data["dose_response_observations"]
            assert de.observation_timepoint is not None
            assert de.endpoint is not None
            assert de.treatment is not None

            if just_created_de_id is None:
                just_created_de_id = de_id

        def altered_de_test(resp):
            nonlocal just_created_de_id

            de_id = resp.json()["id"]
            de = models.DataExtraction.objects.get(id=de_id)
            assert de.dose_response_observations == "test update"
            assert de_id == just_created_de_id

        def deleted_de_test(resp):
            nonlocal just_created_de_id

            assert resp.data is None

            with pytest.raises(ObjectDoesNotExist):
                models.DataExtraction.objects.get(id=just_created_de_id)

        create_scenarios = (
            {
                "desc": "de create",
                "expected_code": 201,
                "expected_keys": {
                    "experiment",
                    "endpoint",
                    "treatment",
                    "observation_timepoint",
                    "dose_response_observations",
                },
                "data": data,
                "post_request_test": de_create_test,
            },
        )
        #
        generic_test_scenarios(client, url, create_scenarios)

        browse_scenarios = (
            {
                "desc": "data extraction browse",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(2),
                "url": f"{url}?assessment_id={db_keys.assessment_working}",
            },
            {
                "desc": "data extraction browse on other assessment",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(0),
                "url": f"{url}?assessment_id={db_keys.assessment_client}",
            },
            {
                "desc": "data extraction browse with good experiment filter",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(2),
                "url": f"{url}?assessment_id={db_keys.assessment_working}&experiment={db_keys.animalv2_experiment}",
            },
            {
                "desc": "data extraction browse with bad experiment filter",
                "expected_code": 400,
                "expected_keys": {"experiment"},
                "expected_content": "invalid_choice",
                "method": "GET",
                "url": f"{url}?assessment_id={db_keys.assessment_working}&experiment=777",
            },
            {
                "desc": "data extraction browse without assessment id",
                "expected_code": 400,
                "method": "GET",
                "expected_content": "Please provide an `assessment_id` argument",
                "url": url,
            },
        )
        generic_test_scenarios(client, None, browse_scenarios)

        update_scenarios = (
            {
                "desc": "de update",
                "expected_code": 200,
                "expected_keys": {
                    "experiment",
                    "endpoint",
                    "treatment",
                    "observation_timepoint",
                    "dose_response_observations",
                },
                "data": {"dose_response_observations": "test update"},
                "method": "PATCH",
                "post_request_test": altered_de_test,
            },
        )
        url = f"{url}{just_created_de_id}/"
        generic_test_scenarios(client, url, update_scenarios)

        read_scenarios = (
            {
                "desc": "de read",
                "expected_code": 200,
                "expected_keys": {
                    "experiment",
                    "endpoint",
                    "treatment",
                    "observation_timepoint",
                    "dose_response_observations",
                },
                "method": "GET",
            },
        )
        generic_test_scenarios(client, url, read_scenarios)

        delete_scenarios = (
            {
                "desc": "de delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_de_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)

    def test_bad_requests(self, db_keys):
        url = reverse("animalv2:api:data-extraction-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        admin_client = APIClient()
        admin_client.login(username="admin@hawcproject.org", password="pw")

        # make another experiment...
        alt_experiment_id = None

        def post_experiment_create(resp):
            nonlocal alt_experiment_id
            alt_experiment_id = resp.json()["id"]

        experiment_url = reverse("animalv2:api:experiment-list")
        generic_test_scenario(
            admin_client,
            experiment_url,
            {
                "desc": "alt experiment create",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": {
                    "study": db_keys.study_final_bioassay,
                    "name": "Dummy Experiment",
                    "design": "AA",
                    "has_multiple_generations": False,
                    "guideline_compliance": "test gl comp",
                    "comments": "test comments",
                },
                "post_request_test": post_experiment_create,
            },
        )

        # ...and another endpoint
        alt_endpoint_id = None

        def post_endpoint_create(resp):
            nonlocal alt_endpoint_id
            alt_endpoint_id = resp.json()["id"]

        endpoint_url = reverse("animalv2:api:endpoint-list")
        generic_test_scenario(
            admin_client,
            endpoint_url,
            {
                "desc": "alt endpoint create",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": {
                    "experiment": db_keys.animalv2_experiment,
                    "name": "Test Endpoint",
                },
                "post_request_test": post_endpoint_create,
            },
        )

        endpoint = generic_get_any(models.Endpoint)
        treatment = generic_get_any(models.Treatment)
        obstime = generic_get_any(models.ObservationTime)

        good_data = {
            "experiment": db_keys.animalv2_experiment,
            "endpoint": endpoint.id,
            "treatment": treatment.id,
            "observation_timepoint": obstime.id,
            "result_details": "test details",
            "dose_response_observations": "test observations",
            "method_to_control_for_litter_effects": constants.MethodToControlForLitterEffects.YES,
            "dataset_type": constants.DatasetType.NOT_REPORTED,
        }

        scenarios = (
            {
                "desc": "invalid endpoint",
                "expected_code": 400,
                "expected_keys": {"endpoint"},
                "expected_content": "does not exist",
                "data": {"endpoint": 999},
            },
            {
                "desc": "invalid treatment",
                "expected_code": 400,
                "expected_keys": {"treatment"},
                "expected_content": "does not exist",
                "data": {"treatment": 999},
            },
            {
                "desc": "invalid obstime",
                "expected_code": 400,
                "expected_keys": {"observation_timepoint"},
                "expected_content": "does not exist",
                "data": {"observation_timepoint": 999},
            },
            {
                "desc": "missing req'd fields",
                "expected_code": 400,
                "expected_keys": {
                    "experiment",
                    "endpoint",
                    "treatment",
                    "dataset_type",
                },
                "expected_content": "required",
                "data": {},
            },
            {
                "desc": "test experiment mismatch",
                "expected_code": 400,
                "expected_keys": {"general"},
                "expected_content": "Endpoint/Treatment/Experiment mismatch",
                "data": clone_and_change(good_data, experiment=alt_experiment_id),
            },
            {
                "desc": "test endpoint/obstime mismatch",
                "expected_code": 400,
                "expected_keys": {"general"},
                "expected_content": "Observation Time/Endpoint mismatch",
                "data": clone_and_change(good_data, endpoint=alt_endpoint_id),
            },
            {
                "desc": "bad dataset type",
                "expected_code": 400,
                "expected_keys": {"dataset_type"},
                "expected_content": "not a valid choice",
                "data": clone_and_change(good_data, dataset_type="xxx"),
            },
            {
                "desc": "bad variance type",
                "expected_code": 400,
                "expected_keys": {"variance_type"},
                "expected_content": "not a valid choice",
                "data": clone_and_change(good_data, variance_type="xxx"),
            },
            {
                "desc": "bad method_to_control_for_litter_effects",
                "expected_code": 400,
                "expected_keys": {"method_to_control_for_litter_effects"},
                "expected_content": "not a valid choice",
                "data": clone_and_change(good_data, method_to_control_for_litter_effects="xxx"),
            },
        )
        generic_test_scenarios(client, url, scenarios)


@pytest.mark.django_db
class TestDoseResponseGroupLevelDataViewSet:
    def test_permissions(self, db_keys):
        url = reverse("animalv2:api:dose-response-group-level-data-list")

        extraction = generic_get_any(models.DataExtraction)

        data = {
            "data_extraction": extraction.id,
            "treatment_name": "Test DRGLD",
            "treatment_related_effect": constants.TreatmentRelatedEffect.YES,
            "dose": "test dose",
            "response": 45.45,
            "variance": 3.14,
            "statistically_significant": constants.StatisticallySignificant.YES,
            "p_value": "p",
            "NOEL": 56,
            "LOEL": 23,
        }

        generic_perm_tester(url, data)

    def test_valid_requests(self, db_keys):
        url = reverse("animalv2:api:dose-response-group-level-data-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        extraction = generic_get_any(models.DataExtraction)

        data = {
            "data_extraction": extraction.id,
            "treatment_name": "Test DRGLD",
            "treatment_related_effect": constants.TreatmentRelatedEffect.YES,
            "dose": "test dose",
            "response": 45.45,
            "variance": 3.14,
            "statistically_significant": constants.StatisticallySignificant.YES,
            "p_value": "p",
            "NOEL": 56,
            "LOEL": 23,
        }

        just_created_drgld_id = None

        def drgld_create_test(resp):
            nonlocal just_created_drgld_id

            drgld_id = resp.json()["id"]
            drgld = models.DoseResponseGroupLevelData.objects.get(id=drgld_id)
            assert drgld.treatment_name == data["treatment_name"]

            if just_created_drgld_id is None:
                just_created_drgld_id = drgld_id

        def altered_drgld_test(resp):
            nonlocal just_created_drgld_id

            drgld_id = resp.json()["id"]
            drgld = models.DoseResponseGroupLevelData.objects.get(id=drgld_id)
            assert drgld.treatment_name == "updated"
            assert drgld_id == just_created_drgld_id

        def deleted_drgld_test(resp):
            nonlocal just_created_drgld_id

            assert resp.data is None

            with pytest.raises(ObjectDoesNotExist):
                models.DoseResponseGroupLevelData.objects.get(id=just_created_drgld_id)

        create_scenarios = (
            {
                "desc": "dose-response-group-level-data create",
                "expected_code": 201,
                "expected_keys": {"id", "treatment_name", "dose", "response", "NOEL"},
                "data": data,
                "post_request_test": drgld_create_test,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        browse_scenarios = (
            {
                "desc": "drgld browse",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(2),
                "url": f"{url}?assessment_id={db_keys.assessment_working}",
            },
            {
                "desc": "drgld browse on other assessment",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(0),
                "url": f"{url}?assessment_id={db_keys.assessment_client}",
            },
            {
                "desc": "drgld browse with good dataextraction filter",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(2),
                "url": f"{url}?assessment_id={db_keys.assessment_working}&data_extraction={extraction.id}",
            },
            {
                "desc": "drgld browse with bad dataextraction filter",
                "expected_code": 400,
                "expected_keys": {"data_extraction"},
                "expected_content": "invalid_choice",
                "method": "GET",
                "url": f"{url}?assessment_id={db_keys.assessment_working}&data_extraction=222",
            },
            {
                "desc": "drgld browse without assessment id",
                "expected_code": 400,
                "method": "GET",
                "expected_content": "Please provide an `assessment_id` argument",
                "url": url,
            },
        )
        generic_test_scenarios(client, None, browse_scenarios)

        update_scenarios = (
            {
                "desc": "dose-response-group-level-data update",
                "expected_code": 200,
                "expected_keys": {"id", "treatment_name", "dose", "response", "NOEL"},
                "data": {"treatment_name": "updated"},
                "method": "PATCH",
                "post_request_test": altered_drgld_test,
            },
        )
        url = f"{url}{just_created_drgld_id}/"
        generic_test_scenarios(client, url, update_scenarios)

        read_scenarios = (
            {
                "desc": "dose-response-group-level-data read",
                "expected_code": 200,
                "expected_keys": {"id", "treatment_name", "dose", "response", "NOEL"},
                "method": "GET",
            },
        )
        generic_test_scenarios(client, url, read_scenarios)

        delete_scenarios = (
            {
                "desc": "dose-response-group-level-data delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_drgld_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)

    def test_bad_requests(self, db_keys):
        url = reverse("animalv2:api:dose-response-group-level-data-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        scenarios = (
            {
                "desc": "invalid data_Extraction",
                "expected_code": 400,
                "expected_keys": {"data_extraction"},
                "expected_content": "does not exist",
                "data": {"data_extraction": 999},
            },
            {
                "desc": "bad treatment_related_effect",
                "expected_code": 400,
                "expected_keys": {"treatment_related_effect"},
                "expected_content": "not a valid choice",
                "data": {"treatment_related_effect": "invalid"},
            },
        )

        generic_test_scenarios(client, url, scenarios)


@pytest.mark.django_db
class TestDoseResponseAnimalLevelDataViewSet:
    def test_permissions(self, db_keys):
        url = reverse("animalv2:api:dose-response-animal-level-data-list")

        extraction = generic_get_any(models.DataExtraction)

        data = {
            "data_extraction": extraction.id,
            "cage_id": "test cage",
            "animal_id": "test ani",
            "dose": "test dose",
            "response": 55.66,
        }

        generic_perm_tester(url, data)

    def test_valid_requests(self, db_keys):
        url = reverse("animalv2:api:dose-response-animal-level-data-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        extraction = generic_get_any(models.DataExtraction)

        data = {
            "data_extraction": extraction.id,
            "cage_id": "test cage",
            "animal_id": "test ani",
            "dose": "test dose",
            "response": 55.66,
        }

        just_created_drald_id = None

        def drald_create_test(resp):
            nonlocal just_created_drald_id

            drald_id = resp.json()["id"]
            drald = models.DoseResponseAnimalLevelData.objects.get(id=drald_id)
            assert drald.animal_id == data["animal_id"]

            if just_created_drald_id is None:
                just_created_drald_id = drald_id

        def altered_drald_test(resp):
            nonlocal just_created_drald_id

            drald_id = resp.json()["id"]
            drald = models.DoseResponseAnimalLevelData.objects.get(id=drald_id)
            assert drald.animal_id == "updated"
            assert drald_id == just_created_drald_id

        def deleted_drald_test(resp):
            nonlocal just_created_drald_id

            assert resp.data is None

            with pytest.raises(ObjectDoesNotExist):
                models.DoseResponseAnimalLevelData.objects.get(id=just_created_drald_id)

        create_scenarios = (
            {
                "desc": "dose-response-animal-level-data create",
                "expected_code": 201,
                "expected_keys": {
                    "id",
                    "data_extraction",
                    "cage_id",
                    "animal_id",
                    "dose",
                    "response",
                },
                "data": data,
                "post_request_test": drald_create_test,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        browse_scenarios = (
            {
                "desc": "drald browse",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(2),
                "url": f"{url}?assessment_id={db_keys.assessment_working}",
            },
            {
                "desc": "drald browse on other assessment",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(0),
                "url": f"{url}?assessment_id={db_keys.assessment_client}",
            },
            {
                "desc": "drald browse with good dataextraction filter",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(2),
                "url": f"{url}?assessment_id={db_keys.assessment_working}&data_extraction={extraction.id}",
            },
            {
                "desc": "drald browse with bad dataextraction filter",
                "expected_code": 400,
                "expected_keys": {"data_extraction"},
                "expected_content": "invalid_choice",
                "method": "GET",
                "url": f"{url}?assessment_id={db_keys.assessment_working}&data_extraction=111",
            },
            {
                "desc": "drald browse without assessment id",
                "expected_code": 400,
                "method": "GET",
                "expected_content": "Please provide an `assessment_id` argument",
                "url": url,
            },
        )
        generic_test_scenarios(client, None, browse_scenarios)

        update_scenarios = (
            {
                "desc": "dose-response-animal-level-data update",
                "expected_code": 200,
                "expected_keys": {
                    "id",
                    "data_extraction",
                    "cage_id",
                    "animal_id",
                    "dose",
                    "response",
                },
                "data": {"animal_id": "updated"},
                "method": "PATCH",
                "post_request_test": altered_drald_test,
            },
        )
        url = f"{url}{just_created_drald_id}/"
        generic_test_scenarios(client, url, update_scenarios)

        read_scenarios = (
            {
                "desc": "dose-response-animal-level-data read",
                "expected_code": 200,
                "expected_keys": {
                    "id",
                    "data_extraction",
                    "cage_id",
                    "animal_id",
                    "dose",
                    "response",
                },
                "method": "GET",
            },
        )
        generic_test_scenarios(client, url, read_scenarios)

        delete_scenarios = (
            {
                "desc": "dose-response-animal-level-data delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_drald_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)

    def test_bad_requests(self, db_keys):
        url = reverse("animalv2:api:dose-response-animal-level-data-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        scenarios = (
            {
                "desc": "invalid data_Extraction",
                "expected_code": 400,
                "expected_keys": {"data_extraction"},
                "expected_content": "does not exist",
                "data": {"data_extraction": 999},
            },
        )

        generic_test_scenarios(client, url, scenarios)


@pytest.mark.django_db
class TestStudyLevelValueViewSet:
    def test_permissions(self, db_keys):
        url = reverse("animalv2:api:study-level-value-list")
        dose_units = generic_get_any(DoseUnits)
        data = {
            "study": db_keys.study_working,
            "value_type": constants.StudyLevelTypeChoices.LOEL,
            "units": dose_units.name,
            "system": "Dummy System",
            "value": 100.3,
            "comments": "test comment",
        }
        generic_perm_tester(url, data)

    def test_valid_requests(self, db_keys):
        url = reverse("animalv2:api:study-level-value-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        dose_units = generic_get_any(DoseUnits)
        data = {
            "study": db_keys.study_working,
            "value_type": constants.StudyLevelTypeChoices.LOEL,
            "units": dose_units.name,
            "system": "Dummy System",
            "value": 100.3,
            "comments": "test comment",
        }

        just_created_slv_id = None

        def slv_create_test(resp):
            nonlocal just_created_slv_id

            slv_id = resp.json()["id"]
            slv = models.StudyLevelValue.objects.get(id=slv_id)
            assert slv.comments == data["comments"]

            if just_created_slv_id is None:
                just_created_slv_id = slv_id

        def altered_slv_test(resp):
            nonlocal just_created_slv_id

            slv_id = resp.json()["id"]
            slv = models.StudyLevelValue.objects.get(id=slv_id)
            assert slv.comments == "slv update"
            assert slv_id == just_created_slv_id

        def deleted_slv_test(resp):
            nonlocal just_created_slv_id

            assert resp.data is None

            with pytest.raises(ObjectDoesNotExist):
                models.StudyLevelValue.objects.get(id=just_created_slv_id)

        create_scenarios = (
            {
                "desc": "slv create",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": data,
                "post_request_test": slv_create_test,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        browse_scenarios = (
            {
                "desc": "slv browse",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(1),
                "url": f"{url}?assessment_id={db_keys.assessment_working}",
            },
            {
                "desc": "slv browse on other assessment",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(0),
                "url": f"{url}?assessment_id={db_keys.assessment_client}",
            },
            {
                "desc": "slv browse with good study filter",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(1),
                "url": f"{url}?assessment_id={db_keys.assessment_working}&study={db_keys.study_working}",
            },
            {
                "desc": "slv browse with bad study filter",
                "expected_code": 200,
                "expected_keys": {"count", "results"},
                "method": "GET",
                "post_request_test": generate_browse_checker(0),
                "url": f"{url}?assessment_id={db_keys.assessment_working}&study={db_keys.study_final_bioassay}",
            },
            {
                "desc": "slv browse without assessment id",
                "expected_code": 400,
                "method": "GET",
                "expected_content": "Please provide an `assessment_id` argument",
                "url": url,
            },
        )
        generic_test_scenarios(client, None, browse_scenarios)

        update_scenarios = (
            {
                "desc": "slv update",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {"comments": "slv update"},
                "method": "PATCH",
                "post_request_test": altered_slv_test,
            },
        )
        url = f"{url}{just_created_slv_id}/"
        generic_test_scenarios(client, url, update_scenarios)

        read_scenarios = (
            {
                "desc": "slv read",
                "expected_code": 200,
                "expected_keys": {"id", "study", "comments"},
                "method": "GET",
            },
        )
        generic_test_scenarios(client, url, read_scenarios)

        delete_scenarios = (
            {
                "desc": "slv delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_slv_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)

        # test API filtering by study id
        # make a dummy study (so we have something else in the assessment to filter by)
        cloned_study = Study.objects.get(id=db_keys.study_working)
        cloned_study.id = None
        cloned_study.pk = None
        cloned_study.save()

        assert cloned_study.id is not None and cloned_study.id != db_keys.study_working
        url = (
            reverse("animalv2:api:study-level-value-list")
            + f"?assessment_id={cloned_study.assessment_id}"
        )

        resp = client.get(url)
        num_experiments_in_assessment = resp.data["count"]

        resp = client.get(url + f"&study={db_keys.study_working}")
        num_experiments_on_study = resp.data["count"]

        resp = client.get(url + f"&study={cloned_study.id}")
        num_experiments_on_other_study = resp.data["count"]

        assert num_experiments_in_assessment == num_experiments_on_study
        assert num_experiments_on_other_study == 0

    def test_bad_requests(self, db_keys):
        url = reverse("animalv2:api:study-level-value-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        scenarios = (
            {
                "desc": "invalid value type",
                "expected_code": 400,
                "expected_keys": {"value_type"},
                "expected_content": "not a valid choice",
                "data": {"value_type": "---"},
            },
        )

        generic_test_scenarios(client, url, scenarios)


def check_details_of_last_log_entry(obj_id: int, start_of_msg: str):
    """
    retrieve the latest log entry and check that the object_id/message look right.
    """
    log_entry = Log.objects.latest("id")
    assert log_entry.object_id == int(obj_id) and log_entry.message.startswith(start_of_msg)


def generic_test_scenarios(client, url, scenarios):
    for scenario in scenarios:
        generic_test_scenario(client, url, scenario)


def generic_test_scenario(client, url, scenario):
    if "url" in scenario:
        url = scenario["url"]

    method = scenario.get("method", "POST")
    if method.upper() == "POST":
        response = client.post(url, scenario["data"], format="json")
    elif method.upper() == "PATCH":
        response = client.patch(url, scenario["data"], format="json")
    elif method.upper() == "DELETE":
        response = client.delete(url)
    elif method.upper() == "GET":
        response = client.get(url, format="json")
    else:
        raise ValueError("Unknown method")

    """
    print(f"\n###### START: '{scenario["desc"]}' ({response.status_code}) ######")
    print(scenario["data"] if "data" in scenario else "(no data)")
    print("----------")
    print(response.data)
    print(f"###### END: '{scenario["desc"]}' ######\n")
    """

    if "expected_code" in scenario:
        assert response.status_code == scenario["expected_code"]

    if "expected_keys" in scenario:
        assert (scenario["expected_keys"]).issubset(response.data.keys())

    if "expected_content" in scenario:
        assert str(response.data).lower().find(scenario["expected_content"].lower()) != -1

    if "post_request_test" in scenario:
        scenario["post_request_test"](response)

    # make sure the audit/log table is getting updated while we're at it
    if response.status_code in [200, 201, 204]:  # successful create/update/delete:
        if method.upper() == "POST":
            check_details_of_last_log_entry(response.data["id"], "Created")
        elif method.upper() == "PATCH":
            check_details_of_last_log_entry(response.data["id"], "Updated")
        elif method.upper() == "DELETE":
            # get the id from the url, e.g. "/epi/api/study-population/2/"
            deleted_id = url.strip("/").split("/")[-1]
            check_details_of_last_log_entry(deleted_id, "Deleted")


def generic_perm_tester(url, data):
    # Reviewers shouldn't be able to create
    client = APIClient()
    assert client.login(username="reviewer@hawcproject.org", password="pw") is True
    response = client.post(url, data, format="json")

    assert response.status_code == 403

    # Public shouldn't be able to create
    client = APIClient()
    response = client.post(url, data, format="json")

    assert response.status_code == 403
