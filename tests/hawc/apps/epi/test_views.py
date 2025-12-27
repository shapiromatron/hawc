import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from ..test_utils import check_200, get_client


@pytest.mark.django_db
def test_get_200():
    client = get_client("admin")
    main = 1
    secondary = 4
    urls = [
        # heatmap
        reverse("epi:heatmap_study_design", args=(main,)),
        reverse("epi:heatmap_results", args=(main,)),
        # criteria
        reverse("epi:studycriteria_create", args=(main,)),
        # adjustment factors
        reverse("epi:adjustmentfactor_create", args=(main,)),
        # study population
        reverse("epi:sp_create", args=(main,)),
        reverse("epi:sp_copy", args=(main,)),
        reverse("epi:sp_detail", args=(main,)),
        reverse("epi:sp_update", args=(main,)),
        reverse("epi:sp_delete", args=(main,)),
        # exposure
        reverse("epi:exp_create", args=(main,)),
        reverse("epi:exp_copy", args=(main,)),
        reverse("epi:exp_detail", args=(main,)),
        reverse("epi:exp_update", args=(main,)),
        reverse("epi:exp_delete", args=(main,)),
        # outcome
        reverse("epi:outcome_list", args=(main,)),
        reverse("epi:outcome_create", args=(main,)),
        reverse("epi:outcome_copy", args=(main,)),
        reverse("epi:outcome_detail", args=(secondary,)),
        reverse("epi:outcome_update", args=(secondary,)),
        reverse("epi:outcome_delete", args=(secondary,)),
        # results
        reverse("epi:result_create", args=(secondary,)),
        reverse("epi:result_copy", args=(secondary,)),
        reverse("epi:result_detail", args=(main,)),
        reverse("epi:result_update", args=(main,)),
        reverse("epi:result_delete", args=(main,)),
        # comparison set
        reverse("epi:cs_create", args=(main,)),
        reverse("epi:cs_copy", args=(main,)),
        reverse("epi:cs_outcome_create", args=(secondary,)),
        reverse("epi:cs_outcome_copy", args=(secondary,)),
        reverse("epi:cs_detail", args=(main,)),
        reverse("epi:cs_update", args=(main,)),
        reverse("epi:cs_delete", args=(main,)),
        # groups
        reverse("epi:g_detail", args=(main,)),
        reverse("epi:g_update", args=(main,)),
    ]
    for url in urls:
        check_200(client, url)


@pytest.mark.django_db
def test_post_200():
    _payloads = {
        "epi_result": {
            "name": "partial PTSD",
            "comparison_set": "1",
            "metric": "2",
            "metric_description": "count",
            "metric_units": "#",
            "data_location": "Table 2",
            "population_description": "",
            "dose_response": "0",
            "dose_response_details": "",
            "prevalence_incidence": "",
            "statistical_power": "0",
            "statistical_power_details": "",
            "statistical_test_results": "",
            "trend_test": "",
            "estimate_type": "0",
            "variance_type": "0",
            "ci_units": "0.95",
            "resulttags": "2",
            "comments": "",
            "form-TOTAL_FORMS": "3",
            "form-INITIAL_FORMS": "3",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-id": "1",
            "form-0-group": "1",
            "form-0-n": "283",
            "form-0-estimate": "20.0",
            "form-0-variance": "",
            "form-0-lower_ci": "",
            "form-0-upper_ci": "",
            "form-0-lower_range": "",
            "form-0-upper_range": "",
            "form-0-p_value_qualifier": " ",
            "form-0-p_value": "",
            "form-0-main_finding_support": "3",
            "form-1-id": "2",
            "form-1-group": "2",
            "form-1-n": "206",
            "form-1-estimate": "15.0",
            "form-1-variance": "",
            "form-1-lower_ci": "",
            "form-1-upper_ci": "",
            "form-1-lower_range": "",
            "form-1-upper_range": "",
            "form-1-p_value_qualifier": " ",
            "form-1-p_value": "",
            "form-1-main_finding_support": "3",
            "form-2-id": "3",
            "form-2-group": "3",
            "form-2-n": "191",
            "form-2-estimate": "16.0",
            "form-2-variance": "",
            "form-2-lower_ci": "",
            "form-2-upper_ci": "",
            "form-2-lower_range": "",
            "form-2-upper_range": "",
            "form-2-p_value_qualifier": " ",
            "form-2-p_value": "",
            "form-2-main_finding_support": "3",
        }
    }

    client = get_client("admin")
    requests = [
        (
            reverse("epi:result_create", args=(4,)),
            _payloads["epi_result"],
            "epi/result_detail.html",
        )
    ]
    for url, payload, success_template in requests:
        response = client.post(url, payload, follow=True)
        assert response.status_code == 200
        assertTemplateUsed(response, success_template)


@pytest.mark.django_db
class TestStudyCriteriaCreateView:
    def test_view(self):
        client = get_client("pm")
        assessment_id = 1
        url = reverse("epi:studycriteria_create", args=(assessment_id,))

        response = client.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, "epi/criteria_form.html")

        payload = {
            "assessment": assessment_id,
            "name": "Test Criteria",
            "description": "Test description",
        }
        response = client.post(url, payload, follow=True)
        assert response.status_code == 200
        assert "window.close();" in response.text


@pytest.mark.django_db
class TestStudyPopulation:
    def test_create_delete(self):
        client = get_client("pm")
        payload = dict(
            study=5,
            name="Example",
            design="SE",
            region="Tokyo",
            participant_n=582,
            comments="Descriptions",
            countries=[1],
        )
        url = reverse("epi:sp_create", args=(1,))

        # render GET view
        response = client.get(url + "?initial=1")
        assertTemplateUsed(response, "epi/studypopulation_form.html")

        # confirm POST is successful
        response = client.post(url, payload, follow=True)
        assertTemplateUsed(response, "epi/studypopulation_detail.html")

        # confirm delete successful
        id = response.context["object"].id
        url = reverse("epi:sp_delete", args=(id,))
        assertTemplateUsed(client.post(url, follow=True), "study/study_detail.html")
