import pytest
from django.urls import reverse

from ..test_utils import check_200, get_client

@pytest.mark.django_db
def test_smoke_get():
    client = get_client("admin")
    urls = [
        # heatmap
        reverse("epi:heatmap_study_design", args=(1,)),
        reverse("epi:heatmap_results", args=(1,)),
        # criteria
        reverse("epi:studycriteria_create", args=(1,)),
        # adjustment factors
        reverse("epi:adjustmentfactor_create", args=(1,)),
        # study population
        reverse("epi:sp_create", args=(1,)),
        reverse("epi:sp_copy_selector", args=(1,)),
        reverse("epi:sp_detail", args=(1,)),
        reverse("epi:sp_update", args=(1,)),
        reverse("epi:sp_delete", args=(1,)),
        # exposure
        reverse("epi:exp_create", args=(1,)),
        reverse("epi:exp_copy_selector", args=(1,)),
        reverse("epi:exp_detail", args=(1,)),
        reverse("epi:exp_update", args=(1,)),
        reverse("epi:exp_delete", args=(1,)),
        # outcome
        reverse("epi:outcome_list", args=(1,)),
        reverse("epi:outcome_create", args=(1,)),
        reverse("epi:outcome_copy_selector", args=(1,)),
        reverse("epi:outcome_detail", args=(4,)),
        reverse("epi:outcome_update", args=(4,)),
        reverse("epi:outcome_delete", args=(4,)),
        # results
        reverse("epi:result_create", args=(4,)),
        reverse("epi:result_copy_selector", args=(4,)),
        reverse("epi:result_detail", args=(1,)),
        reverse("epi:result_update", args=(1,)),
        reverse("epi:result_delete", args=(1,)),
        # comparison set
        reverse("epi:cs_create", args=(1,)),
        reverse("epi:cs_copy_selector", args=(1,)),
        reverse("epi:cs_outcome_create", args=(4,)),
        reverse("epi:cs_outcome_copy_selector", args=(4,)),
        reverse("epi:cs_detail", args=(1,)),
        reverse("epi:cs_update", args=(1,)),
        reverse("epi:cs_delete", args=(1,)),
        # groups
        reverse("epi:g_detail", args=(1,)),
        reverse("epi:g_update", args=(1,)),
    ]
    for url in urls:
        check_200(client, url)
