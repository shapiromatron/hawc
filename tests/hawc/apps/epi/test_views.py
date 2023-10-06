import pytest
from django.urls import reverse

from ..test_utils import check_200, get_client


@pytest.mark.django_db
def test_smoke_get():
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
        reverse("epi:sp_copy_selector", args=(main,)),
        reverse("epi:sp_detail", args=(main,)),
        reverse("epi:sp_update", args=(main,)),
        reverse("epi:sp_delete", args=(main,)),
        # exposure
        reverse("epi:exp_create", args=(main,)),
        reverse("epi:exp_copy_selector", args=(main,)),
        reverse("epi:exp_detail", args=(main,)),
        reverse("epi:exp_update", args=(main,)),
        reverse("epi:exp_delete", args=(main,)),
        # outcome
        reverse("epi:outcome_list", args=(main,)),
        reverse("epi:outcome_create", args=(main,)),
        reverse("epi:outcome_copy_selector", args=(main,)),
        reverse("epi:outcome_detail", args=(secondary,)),
        reverse("epi:outcome_update", args=(secondary,)),
        reverse("epi:outcome_delete", args=(secondary,)),
        # results
        reverse("epi:result_create", args=(secondary,)),
        reverse("epi:result_copy_selector", args=(secondary,)),
        reverse("epi:result_detail", args=(main,)),
        reverse("epi:result_update", args=(main,)),
        reverse("epi:result_delete", args=(main,)),
        # comparison set
        reverse("epi:cs_create", args=(main,)),
        reverse("epi:cs_copy_selector", args=(main,)),
        reverse("epi:cs_outcome_create", args=(secondary,)),
        reverse("epi:cs_outcome_copy_selector", args=(secondary,)),
        reverse("epi:cs_detail", args=(main,)),
        reverse("epi:cs_update", args=(main,)),
        reverse("epi:cs_delete", args=(main,)),
        # groups
        reverse("epi:g_detail", args=(main,)),
        reverse("epi:g_update", args=(main,)),
    ]
    for url in urls:
        check_200(client, url)
