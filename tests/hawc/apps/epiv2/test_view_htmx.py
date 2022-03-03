import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from hawc.apps.epiv2 import models


@pytest.mark.django_db
class TestDesignChildren:
    def test_children(self, db_keys):
        design_id = db_keys.epiv2_design
        design = models.Design.objects.get(id=design_id)
        client = Client(HTTP_HX_REQUEST="true")
        assert client.login(email="pm@hawcproject.org", password="pw") is True

        initial_chem_count = models.Chemical.objects.count()
        initial_exposure_count = models.Exposure.objects.count()
        initial_exposurelevel_count = models.ExposureLevel.objects.count()
        initial_outcome_count = models.Outcome.objects.count()
        initial_adjustmentfactor_count = models.AdjustmentFactor.objects.count()
        initial_dataextraction_count = models.DataExtraction.objects.count()

        # chemical create
        url = reverse("epiv2:chemical-create", args=[design.id])
        dsstox_id = models.DSSTox.objects.first().dtxsid
        inputs = {
            "name": "ex chemical",
            "dsstox": dsstox_id,
        }
        with assertTemplateUsed("epiv2/fragments/chemical_row.html"):
            resp = client.post(url, data=inputs)
            assert resp.status_code == 200
            assert "<td>ex chemical</td>" in str(resp.content)
            chemical = resp.context["object"]
            assert f"chemical-{chemical.id}" in str(resp.content)
            assert models.Chemical.objects.count() == initial_chem_count + 1

        # chemical clone
        url = reverse("epiv2:chemical-clone", args=[chemical.id])
        with assertTemplateUsed("epiv2/fragments/chemical_row.html"):
            resp = client.post(url)
            assert resp.status_code == 200
            assert "<td>ex chemical (2)</td>" in str(resp.content)
            assert models.Chemical.objects.count() == initial_chem_count + 2
            chemical_2 = resp.context["object"]

        # chemical read
        url = reverse("epiv2:chemical-detail", args=[chemical.id])
        with assertTemplateUsed("epiv2/fragments/chemical_row.html"):
            resp = client.get(url)
            assert resp.status_code == 200
            assert "<td>ex chemical</td>" in str(resp.content)
            assert models.Chemical.objects.count() == initial_chem_count + 2

        # chemical update
        url = reverse("epiv2:chemical-update", args=[chemical.id])
        dsstox_id = models.DSSTox.objects.first().dtxsid
        inputs = {
            "name": "ex chemical update",
        }
        with assertTemplateUsed("epiv2/fragments/chemical_row.html"):
            resp = client.post(url, data=inputs)
            assert resp.status_code == 200
            assert "<td>ex chemical update</td>" in str(resp.content)
            assert f"chemical-{chemical.id}" in str(resp.content)
            assert models.Chemical.objects.count() == initial_chem_count + 2

        # exposure create
        url = reverse("epiv2:exposure-create", args=[design.id])
        inputs = {
            "name": "ex exposure",
            "measurement_type": "FD",
        }
        with assertTemplateUsed("epiv2/fragments/exposure_row.html"):
            resp = client.post(url, data=inputs)
            assert resp.status_code == 200
            assert "<td>ex exposure</td>" in str(resp.content)
            exposure = resp.context["object"]
            assert f"exposure-{exposure.id}" in str(resp.content)
            assert models.Exposure.objects.count() == initial_exposure_count + 1

        # exposure clone
        url = reverse("epiv2:exposure-clone", args=[exposure.id])
        with assertTemplateUsed("epiv2/fragments/exposure_row.html"):
            resp = client.post(url)
            assert resp.status_code == 200
            assert "<td>ex exposure (2)</td>" in str(resp.content)
            assert models.Exposure.objects.count() == initial_exposure_count + 2
            exposure_2 = resp.context["object"]

        # exposure read
        url = reverse("epiv2:exposure-detail", args=[exposure.id])
        with assertTemplateUsed("epiv2/fragments/exposure_row.html"):
            resp = client.get(url)
            assert resp.status_code == 200
            assert "<td>ex exposure</td>" in str(resp.content)
            assert models.Exposure.objects.count() == initial_exposure_count + 2

        # exposure update
        url = reverse("epiv2:exposure-update", args=[exposure.id])
        inputs = {
            "name": "ex exposure update",
            "measurement_type": "DW",
        }
        with assertTemplateUsed("epiv2/fragments/exposure_row.html"):
            resp = client.post(url, data=inputs)
            assert resp.status_code == 200
            assert "<td>ex exposure update</td>" in str(resp.content)
            assert f"exposure-{exposure.id}" in str(resp.content)
            assert models.Exposure.objects.count() == initial_exposure_count + 2

        # exposure level create
        url = reverse("epiv2:exposurelevel-create", args=[design.id])
        inputs = {
            "name": "ex exposure level",
            "chemical": chemical.id,
            "exposure_measurement": exposure.id,
        }
        with assertTemplateUsed("epiv2/fragments/exposurelevel_row.html"):
            resp = client.post(url, data=inputs)
            assert resp.status_code == 200
            assert "<td>ex exposure level</td>" in str(resp.content)
            exposure_level = resp.context["object"]
            assert (
                f"exposurelevel-{exposure_level.id} chemical-{chemical.id} exposure-{exposure.id}"
                in str(resp.content)
            )
            assert models.ExposureLevel.objects.count() == initial_exposurelevel_count + 1

        # exposure level clone
        url = reverse("epiv2:exposurelevel-clone", args=[exposure_level.id])
        with assertTemplateUsed("epiv2/fragments/exposurelevel_row.html"):
            resp = client.post(url)
            assert resp.status_code == 200
            assert "<td>ex exposure level (2)</td>" in str(resp.content)
            assert models.ExposureLevel.objects.count() == initial_exposurelevel_count + 2
            exposure_level_2 = resp.context["object"]

        # exposure level read
        url = reverse("epiv2:exposurelevel-detail", args=[exposure_level.id])
        with assertTemplateUsed("epiv2/fragments/exposurelevel_row.html"):
            resp = client.get(url)
            assert resp.status_code == 200
            assert "<td>ex exposure level</td>" in str(resp.content)
            assert models.ExposureLevel.objects.count() == initial_exposurelevel_count + 2

        # exposure level update
        url = reverse("epiv2:exposurelevel-update", args=[exposure_level.id])
        inputs = {
            "name": "ex exposure level update",
            "chemical": chemical.id,
            "exposure_measurement": exposure.id,
            "sub_population": "example sub population",
        }
        with assertTemplateUsed("epiv2/fragments/exposurelevel_row.html"):
            resp = client.post(url, data=inputs)
            assert resp.status_code == 200
            assert "<td>ex exposure level update</td>" in str(resp.content)
            assert (
                f"exposurelevel-{exposure_level.id} chemical-{chemical.id} exposure-{exposure.id}"
                in str(resp.content)
            )
            assert models.ExposureLevel.objects.count() == initial_exposurelevel_count + 2

        # outcome create
        url = reverse("epiv2:outcome-create", args=[design.id])
        inputs = {
            "endpoint": "ex outcome",
            "health_outcome": "ex health outcome",
        }
        with assertTemplateUsed("epiv2/fragments/outcome_row.html"):
            resp = client.post(url, data=inputs)
            assert resp.status_code == 200
            assert "<td>ex outcome</td>" in str(resp.content)
            outcome = resp.context["object"]
            assert f"outcome-{outcome.id}" in str(resp.content)
            assert models.Outcome.objects.count() == initial_outcome_count + 1

        # outcome clone
        url = reverse("epiv2:outcome-clone", args=[outcome.id])
        with assertTemplateUsed("epiv2/fragments/outcome_row.html"):
            resp = client.post(url)
            assert resp.status_code == 200
            assert "<td>ex outcome (2)</td>" in str(resp.content)
            assert models.Outcome.objects.count() == initial_outcome_count + 2
            outcome_2 = resp.context["object"]

        # outcome read
        url = reverse("epiv2:outcome-detail", args=[outcome.id])
        with assertTemplateUsed("epiv2/fragments/outcome_row.html"):
            resp = client.get(url)
            assert resp.status_code == 200
            assert "<td>ex outcome</td>" in str(resp.content)
            assert models.Outcome.objects.count() == initial_outcome_count + 2

        # outcome update
        url = reverse("epiv2:outcome-update", args=[outcome.id])
        inputs = {
            "endpoint": "ex outcome update",
            "health_outcome": "ex health outcome update",
        }
        with assertTemplateUsed("epiv2/fragments/outcome_row.html"):
            resp = client.post(url, data=inputs)
            assert resp.status_code == 200
            assert "<td>ex outcome update</td>" in str(resp.content)
            assert f"outcome-{outcome.id}" in str(resp.content)
            assert models.Outcome.objects.count() == initial_outcome_count + 2

        # adjustment factor create
        url = reverse("epiv2:adjustmentfactor-create", args=[design.id])
        inputs = {
            "name": "ex adjustment factor",
        }
        with assertTemplateUsed("epiv2/fragments/adjustment_factor_row.html"):
            resp = client.post(url, data=inputs)
            assert resp.status_code == 200
            assert "<td>ex adjustment factor</td>" in str(resp.content)
            adjust_factor = resp.context["object"]
            assert f"adjustmentfactor-{adjust_factor.id}" in str(resp.content)
            assert models.AdjustmentFactor.objects.count() == initial_adjustmentfactor_count + 1

        # adjustment factor clone
        url = reverse("epiv2:adjustmentfactor-clone", args=[adjust_factor.id])
        with assertTemplateUsed("epiv2/fragments/adjustment_factor_row.html"):
            resp = client.post(url)
            assert resp.status_code == 200
            assert "<td>ex adjustment factor (2)</td>" in str(resp.content)
            assert models.AdjustmentFactor.objects.count() == initial_adjustmentfactor_count + 2
            adjust_factor_2 = resp.context["object"]

        # adjustment factor read
        url = reverse("epiv2:adjustmentfactor-detail", args=[adjust_factor.id])
        with assertTemplateUsed("epiv2/fragments/adjustment_factor_row.html"):
            resp = client.get(url)
            assert resp.status_code == 200
            assert "<td>ex adjustment factor</td>" in str(resp.content)
            assert models.AdjustmentFactor.objects.count() == initial_adjustmentfactor_count + 2

        # adjustment factor update
        url = reverse("epiv2:adjustmentfactor-update", args=[adjust_factor.id])
        inputs = {
            "name": "ex adjustment factor update",
        }
        with assertTemplateUsed("epiv2/fragments/adjustment_factor_row.html"):
            resp = client.post(url, data=inputs)
            assert resp.status_code == 200
            assert "<td>ex adjustment factor update</td>" in str(resp.content)
            assert f"adjustmentfactor-{adjust_factor.id}" in str(resp.content)
            assert models.AdjustmentFactor.objects.count() == initial_adjustmentfactor_count + 2

        # data extraction create
        url = reverse("epiv2:dataextraction-create", args=[design_id])
        inputs = {
            "sub_population": "ex sp",
            "outcome": outcome.id,
            "exposure_level": exposure_level.id,
            "exposure_rank": 1,
            "significant": 2,
            "adjustment_factor": adjust_factor.id,
        }
        with assertTemplateUsed("epiv2/fragments/data_extraction_row.html"):
            resp = client.post(url, data=inputs)
            assert resp.status_code == 200
            assert "<td>ex sp</td>" in str(resp.content)
            assert "<td>ex outcome update</td>" in str(resp.content)
            assert "<td>ex exposure level update</td>" in str(resp.content)
            assert (
                f"outcome-{outcome.id} exposurelevel-{exposure_level.id} chemical-{chemical.id} exposure-{exposure.id} adjustmentfactor-{adjust_factor.id}"
                in str(resp.content)
            )
            assert models.DataExtraction.objects.count() == initial_dataextraction_count + 1
            data_extract = resp.context["object"]

        # data extraction clone
        url = reverse("epiv2:dataextraction-clone", args=[data_extract.id])
        with assertTemplateUsed("epiv2/fragments/data_extraction_row.html"):
            resp = client.post(url)
            assert resp.status_code == 200
            assert models.DataExtraction.objects.count() == initial_dataextraction_count + 2
            data_extract_2 = resp.context["object"]

        # data extraction read
        url = reverse("epiv2:dataextraction-detail", args=[data_extract.id])
        with assertTemplateUsed("epiv2/fragments/data_extraction_row.html"):
            resp = client.get(url)
            assert resp.status_code == 200
            assert "<td>ex sp</td>" in str(resp.content)
            assert "<td>ex outcome update</td>" in str(resp.content)
            assert models.DataExtraction.objects.count() == initial_dataextraction_count + 2

        # data extraction update
        url = reverse("epiv2:dataextraction-update", args=[data_extract.id])
        inputs = {
            "sub_population": "ex sp update",
            "outcome": outcome.id,
            "exposure_level": exposure_level.id,
            "exposure_rank": 4,
            "significant": 1,
            "adjustment_factor": adjust_factor.id,
        }
        with assertTemplateUsed("epiv2/fragments/data_extraction_row.html"):
            resp = client.post(url, data=inputs)
            assert resp.status_code == 200
            assert "<td>ex sp update</td>" in str(resp.content)
            assert "<td>ex outcome update</td>" in str(resp.content)
            assert "<td>ex exposure level update</td>" in str(resp.content)
            assert (
                f"outcome-{outcome.id} exposurelevel-{exposure_level.id} chemical-{chemical.id} exposure-{exposure.id} adjustmentfactor-{adjust_factor.id}"
                in str(resp.content)
            )
            assert models.DataExtraction.objects.count() == initial_dataextraction_count + 2
            assert resp.context["object"].exposure_rank == 4
            assert resp.context["object"].significant == 1

        # data extraction delete
        url = reverse("epiv2:dataextraction-delete", args=[data_extract.id])
        with assertTemplateUsed("epiv2/fragments/_delete_rows.html"):
            resp = client.post(url)
            assert resp.status_code == 200
            assert models.DataExtraction.objects.count() == initial_dataextraction_count + 1
            url = reverse("epiv2:dataextraction-delete", args=[data_extract_2.id])
            resp = client.post(url)
            assert resp.status_code == 200
            assert models.DataExtraction.objects.count() == initial_dataextraction_count

        # adjustment factor delete
        url = reverse("epiv2:adjustmentfactor-delete", args=[adjust_factor.id])
        with assertTemplateUsed("epiv2/fragments/_delete_rows.html"):
            resp = client.post(url)
            assert resp.status_code == 200
            assert models.AdjustmentFactor.objects.count() == initial_adjustmentfactor_count + 1
            url = reverse("epiv2:adjustmentfactor-delete", args=[adjust_factor_2.id])
            resp = client.post(url)
            assert resp.status_code == 200
            assert models.AdjustmentFactor.objects.count() == initial_adjustmentfactor_count

        # outcome delete
        url = reverse("epiv2:outcome-delete", args=[outcome.id])
        with assertTemplateUsed("epiv2/fragments/_delete_rows.html"):
            resp = client.post(url)
            assert resp.status_code == 200
            assert models.Outcome.objects.count() == initial_outcome_count + 1
            url = reverse("epiv2:outcome-delete", args=[outcome_2.id])
            resp = client.post(url)
            assert resp.status_code == 200
            assert models.Outcome.objects.count() == initial_outcome_count

        # exposure level delete
        url = reverse("epiv2:exposurelevel-delete", args=[exposure_level.id])
        with assertTemplateUsed("epiv2/fragments/_delete_rows.html"):
            resp = client.post(url)
            assert resp.status_code == 200
            assert models.ExposureLevel.objects.count() == initial_exposurelevel_count + 1
            url = reverse("epiv2:exposurelevel-delete", args=[exposure_level_2.id])
            resp = client.post(url)
            assert resp.status_code == 200
            assert models.ExposureLevel.objects.count() == initial_exposurelevel_count

        # exposure delete
        url = reverse("epiv2:exposure-delete", args=[exposure.id])
        with assertTemplateUsed("epiv2/fragments/_delete_rows.html"):
            resp = client.post(url)
            assert resp.status_code == 200
            assert models.Exposure.objects.count() == initial_exposure_count + 1
            url = reverse("epiv2:exposure-delete", args=[exposure_2.id])
            resp = client.post(url)
            assert resp.status_code == 200
            assert models.Exposure.objects.count() == initial_exposure_count

        # chemical delete
        url = reverse("epiv2:chemical-delete", args=[chemical.id])
        with assertTemplateUsed("epiv2/fragments/_delete_rows.html"):
            resp = client.post(url)
            assert resp.status_code == 200
            assert models.Chemical.objects.count() == initial_chem_count + 1
            url = reverse("epiv2:chemical-delete", args=[chemical_2.id])
            resp = client.post(url)
            assert resp.status_code == 200
            assert models.Chemical.objects.count() == initial_chem_count
