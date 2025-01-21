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
        client = Client(headers={"hx-request": "true"})
        assert client.login(email="pm@hawcproject.org", password="pw") is True

        initial_chem_count = models.Chemical.objects.count()
        initial_exposure_count = models.Exposure.objects.count()
        initial_exposurelevel_count = models.ExposureLevel.objects.count()
        initial_outcome_count = models.Outcome.objects.count()
        initial_adjustmentfactor_count = models.AdjustmentFactor.objects.count()
        initial_dataextraction_count = models.DataExtraction.objects.count()

        # chemical create
        url = reverse("epiv2:chemical-htmx", args=[design.id, "create"])
        dsstox_id = models.DSSTox.objects.first().dtxsid
        inputs = {
            "chemical-new-name": "ex chemical",
            "chemical-new-dsstox": dsstox_id,
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "epiv2/fragments/chemical_row.html")
        assert resp.status_code == 200
        assert "<td>ex chemical</td>" in str(resp.content)
        chemical = resp.context["object"]
        assert f"chemical-{chemical.id}" in str(resp.content)
        assert models.Chemical.objects.count() == initial_chem_count + 1

        # chemical clone
        url = reverse("epiv2:chemical-htmx", args=[chemical.id, "clone"])
        resp = client.post(url)
        assertTemplateUsed(resp, "epiv2/fragments/chemical_row.html")
        assert resp.status_code == 200
        assert "<td>ex chemical (2)</td>" in str(resp.content)
        assert models.Chemical.objects.count() == initial_chem_count + 2
        chemical_2 = resp.context["object"]

        # chemical read
        url = reverse("epiv2:chemical-htmx", args=[chemical.id, "read"])
        resp = client.get(url)
        assertTemplateUsed(resp, "epiv2/fragments/chemical_row.html")
        assert resp.status_code == 200
        assert "<td>ex chemical</td>" in str(resp.content)
        assert models.Chemical.objects.count() == initial_chem_count + 2

        # chemical update
        url = reverse("epiv2:chemical-htmx", args=[chemical.id, "update"])
        dsstox_id = models.DSSTox.objects.first().dtxsid
        inputs = {
            f"chemical-{chemical.id}-name": "ex chemical update",
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "epiv2/fragments/chemical_row.html")
        assert resp.status_code == 200
        assert "<td>ex chemical update</td>" in str(resp.content)
        assert f"chemical-{chemical.id}" in str(resp.content)
        assert models.Chemical.objects.count() == initial_chem_count + 2

        # exposure create
        url = reverse("epiv2:exposure-htmx", args=[design.id, "create"])
        inputs = {
            "exposure-new-name": "ex exposure",
            "exposure-new-measurement_type_0": ["Food"],
            "exposure-new-exposure_route": "OR",
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "epiv2/fragments/exposure_row.html")
        assert resp.status_code == 200
        assert "<td>ex exposure</td>" in str(resp.content)
        exposure = resp.context["object"]
        assert f"exposure-{exposure.id}" in str(resp.content)
        assert models.Exposure.objects.count() == initial_exposure_count + 1

        # exposure clone
        url = reverse("epiv2:exposure-htmx", args=[exposure.id, "clone"])
        resp = client.post(url)
        assertTemplateUsed(resp, "epiv2/fragments/exposure_row.html")
        assert resp.status_code == 200
        assert "<td>ex exposure (2)</td>" in str(resp.content)
        assert models.Exposure.objects.count() == initial_exposure_count + 2
        exposure_2 = resp.context["object"]

        # exposure read
        url = reverse("epiv2:exposure-htmx", args=[exposure.id, "read"])
        resp = client.get(url)
        assertTemplateUsed(resp, "epiv2/fragments/exposure_row.html")
        assert resp.status_code == 200
        assert "<td>ex exposure</td>" in str(resp.content)
        assert models.Exposure.objects.count() == initial_exposure_count + 2

        # exposure update
        url = reverse("epiv2:exposure-htmx", args=[exposure.id, "update"])
        inputs = {
            f"exposure-{exposure.id}-name": "ex exposure update",
            f"exposure-{exposure.id}-measurement_type_0": ["Drinking water"],
            f"exposure-{exposure.id}-exposure_route": "OR",
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "epiv2/fragments/exposure_row.html")
        assert resp.status_code == 200
        assert "<td>ex exposure update</td>" in str(resp.content)
        assert f"exposure-{exposure.id}" in str(resp.content)
        assert models.Exposure.objects.count() == initial_exposure_count + 2

        # exposure level create
        url = reverse("epiv2:exposurelevel-htmx", args=[design.id, "create"])
        inputs = {
            "exposurelevel-new-name": "ex exposure level",
            "exposurelevel-new-chemical": chemical.id,
            "exposurelevel-new-exposure_measurement": exposure.id,
            "exposurelevel-new-variance_type": 0,
            "exposurelevel-new-ci_type": "Rng",
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "epiv2/fragments/exposurelevel_row.html")
        assert resp.status_code == 200
        assert "<td>ex exposure level</td>" in str(resp.content)
        exposure_level = resp.context["object"]
        assert (
            f"exposurelevel-{exposure_level.id} chemical-{chemical.id} exposure-{exposure.id}"
            in str(resp.content)
        )
        assert models.ExposureLevel.objects.count() == initial_exposurelevel_count + 1

        # exposure level clone
        url = reverse("epiv2:exposurelevel-htmx", args=[exposure_level.id, "clone"])
        resp = client.post(url)
        assertTemplateUsed(resp, "epiv2/fragments/exposurelevel_row.html")
        assert resp.status_code == 200
        assert "<td>ex exposure level (2)</td>" in str(resp.content)
        assert models.ExposureLevel.objects.count() == initial_exposurelevel_count + 2
        exposure_level_2 = resp.context["object"]

        # exposure level read
        url = reverse("epiv2:exposurelevel-htmx", args=[exposure_level.id, "read"])
        resp = client.get(url)
        assertTemplateUsed(resp, "epiv2/fragments/exposurelevel_row.html")
        assert resp.status_code == 200
        assert "<td>ex exposure level</td>" in str(resp.content)
        assert models.ExposureLevel.objects.count() == initial_exposurelevel_count + 2

        # exposure level update
        url = reverse("epiv2:exposurelevel-htmx", args=[exposure_level.id, "update"])
        inputs = {
            f"exposurelevel-{exposure_level.id}-name": "ex exposure level update",
            f"exposurelevel-{exposure_level.id}-chemical": chemical.id,
            f"exposurelevel-{exposure_level.id}-exposure_measurement": exposure.id,
            f"exposurelevel-{exposure_level.id}-sub_population": "example sub population",
            f"exposurelevel-{exposure_level.id}-variance_type": 0,
            f"exposurelevel-{exposure_level.id}-ci_type": "Rng",
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "epiv2/fragments/exposurelevel_row.html")
        assert resp.status_code == 200
        assert "<td>ex exposure level update</td>" in str(resp.content)
        assert (
            f"exposurelevel-{exposure_level.id} chemical-{chemical.id} exposure-{exposure.id}"
            in str(resp.content)
        )
        assert models.ExposureLevel.objects.count() == initial_exposurelevel_count + 2

        # outcome create
        url = reverse("epiv2:outcome-htmx", args=[design.id, "create"])
        inputs = {
            "outcome-new-endpoint": "ex outcome",
            "outcome-new-effect": "ex health outcome",
            "outcome-new-system": "CA",
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "epiv2/fragments/outcome_row.html")
        assert resp.status_code == 200
        assert "<td>ex outcome</td>" in str(resp.content)
        outcome = resp.context["object"]
        assert f"outcome-{outcome.id}" in str(resp.content)
        assert models.Outcome.objects.count() == initial_outcome_count + 1

        # outcome clone
        url = reverse("epiv2:outcome-htmx", args=[outcome.id, "clone"])
        resp = client.post(url)
        assertTemplateUsed(resp, "epiv2/fragments/outcome_row.html")
        assert resp.status_code == 200
        assert "<td>ex outcome (2)</td>" in str(resp.content)
        assert models.Outcome.objects.count() == initial_outcome_count + 2
        outcome_2 = resp.context["object"]

        # outcome read
        url = reverse("epiv2:outcome-htmx", args=[outcome.id, "read"])
        resp = client.get(url)
        assertTemplateUsed(resp, "epiv2/fragments/outcome_row.html")
        assert resp.status_code == 200
        assert "<td>ex outcome</td>" in str(resp.content)
        assert models.Outcome.objects.count() == initial_outcome_count + 2

        # outcome update
        url = reverse("epiv2:outcome-htmx", args=[outcome.id, "update"])
        inputs = {
            f"outcome-{outcome.id}-endpoint": "ex outcome update",
            f"outcome-{outcome.id}-effect": "ex health outcome update",
            f"outcome-{outcome.id}-system": "CA",
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "epiv2/fragments/outcome_row.html")
        assert resp.status_code == 200
        assert "<td>ex outcome update</td>" in str(resp.content)
        assert f"outcome-{outcome.id}" in str(resp.content)
        assert models.Outcome.objects.count() == initial_outcome_count + 2

        # adjustment factor create
        url = reverse("epiv2:adjustmentfactor-htmx", args=[design.id, "create"])
        inputs = {
            "adjustmentfactor-new-name": "ex adjustment factor",
            "adjustmentfactor-new-description": "smoking, drinking",
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "epiv2/fragments/adjustment_factor_row.html")
        assert resp.status_code == 200
        assert "<td>ex adjustment factor</td>" in str(resp.content)
        adjust_factor = resp.context["object"]
        assert f"adjustmentfactor-{adjust_factor.id}" in str(resp.content)
        assert models.AdjustmentFactor.objects.count() == initial_adjustmentfactor_count + 1

        # adjustment factor clone
        url = reverse("epiv2:adjustmentfactor-htmx", args=[adjust_factor.id, "clone"])
        resp = client.post(url)
        assertTemplateUsed(resp, "epiv2/fragments/adjustment_factor_row.html")
        assert resp.status_code == 200
        assert "<td>ex adjustment factor (2)</td>" in str(resp.content)
        assert models.AdjustmentFactor.objects.count() == initial_adjustmentfactor_count + 2
        adjust_factor_2 = resp.context["object"]

        # adjustment factor read
        url = reverse("epiv2:adjustmentfactor-htmx", args=[adjust_factor.id, "read"])
        resp = client.get(url)
        assertTemplateUsed(resp, "epiv2/fragments/adjustment_factor_row.html")
        assert resp.status_code == 200
        assert "<td>ex adjustment factor</td>" in str(resp.content)
        assert models.AdjustmentFactor.objects.count() == initial_adjustmentfactor_count + 2

        # adjustment factor update
        url = reverse("epiv2:adjustmentfactor-htmx", args=[adjust_factor.id, "update"])
        inputs = {
            f"adjustmentfactor-{adjust_factor.id}-name": "ex adjustment factor update",
            f"adjustmentfactor-{adjust_factor.id}-description": "smoking, drinking, dancing",
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "epiv2/fragments/adjustment_factor_row.html")
        assert resp.status_code == 200
        assert "<td>ex adjustment factor update</td>" in str(resp.content)
        assert f"adjustmentfactor-{adjust_factor.id}" in str(resp.content)
        assert models.AdjustmentFactor.objects.count() == initial_adjustmentfactor_count + 2

        # data extraction create
        url = reverse("epiv2:dataextraction-htmx", args=[design_id, "create"])
        inputs = {
            "dataextraction-new-group": "ex sp",
            "dataextraction-new-outcome": outcome.id,
            "dataextraction-new-exposure_level": exposure_level.id,
            "dataextraction-new-effect_estimate_type": "OR",
            "dataextraction-new-effect_estimate": 1.5,
            "dataextraction-new-exposure_rank": 1,
            "dataextraction-new-significant": 2,
            "dataextraction-new-factors": adjust_factor.id,
            "dataextraction-new-variance_type": 0,
            "dataextraction-new-ci_type": "Rng",
            "dataextraction-new-adverse_direction": "unspecified",
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "epiv2/fragments/data_extraction_row.html")
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
        url = reverse("epiv2:dataextraction-htmx", args=[data_extract.id, "clone"])
        resp = client.post(url)
        assertTemplateUsed(resp, "epiv2/fragments/data_extraction_row.html")
        assert resp.status_code == 200
        assert models.DataExtraction.objects.count() == initial_dataextraction_count + 2
        data_extract_2 = resp.context["object"]

        # data extraction read
        url = reverse("epiv2:dataextraction-htmx", args=[data_extract.id, "read"])
        resp = client.get(url)
        assertTemplateUsed(resp, "epiv2/fragments/data_extraction_row.html")
        assert resp.status_code == 200
        assert "<td>ex sp</td>" in str(resp.content)
        assert "<td>ex outcome update</td>" in str(resp.content)
        assert models.DataExtraction.objects.count() == initial_dataextraction_count + 2

        # data extraction update
        url = reverse("epiv2:dataextraction-htmx", args=[data_extract.id, "update"])
        inputs = {
            f"dataextraction-{data_extract.id}-group": "ex sp update",
            f"dataextraction-{data_extract.id}-outcome": outcome.id,
            f"dataextraction-{data_extract.id}-exposure_level": exposure_level.id,
            f"dataextraction-{data_extract.id}-effect_estimate_type": "OR",
            f"dataextraction-{data_extract.id}-effect_estimate": 2.5,
            f"dataextraction-{data_extract.id}-exposure_rank": 4,
            f"dataextraction-{data_extract.id}-significant": 1,
            f"dataextraction-{data_extract.id}-factors": adjust_factor.id,
            f"dataextraction-{data_extract.id}-variance_type": 1,
            f"dataextraction-{data_extract.id}-ci_type": "P95",
            f"dataextraction-{data_extract.id}-adverse_direction": "unspecified",
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "epiv2/fragments/data_extraction_row.html")
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
        url = reverse("epiv2:dataextraction-htmx", args=[data_extract.id, "delete"])
        resp = client.post(url)
        assertTemplateUsed(resp, "common/fragments/_delete_rows.html")
        assert resp.status_code == 200
        assert models.DataExtraction.objects.count() == initial_dataextraction_count + 1
        url = reverse("epiv2:dataextraction-htmx", args=[data_extract_2.id, "delete"])
        resp = client.post(url)
        assert resp.status_code == 200
        assert models.DataExtraction.objects.count() == initial_dataextraction_count

        # adjustment factor delete
        url = reverse("epiv2:adjustmentfactor-htmx", args=[adjust_factor.id, "delete"])
        resp = client.post(url)
        assertTemplateUsed(resp, "common/fragments/_delete_rows.html")
        assert resp.status_code == 200
        assert models.AdjustmentFactor.objects.count() == initial_adjustmentfactor_count + 1
        url = reverse("epiv2:adjustmentfactor-htmx", args=[adjust_factor_2.id, "delete"])
        resp = client.post(url)
        assert resp.status_code == 200
        assert models.AdjustmentFactor.objects.count() == initial_adjustmentfactor_count

        # outcome delete
        url = reverse("epiv2:outcome-htmx", args=[outcome.id, "delete"])
        resp = client.post(url)
        assertTemplateUsed(resp, "common/fragments/_delete_rows.html")
        assert resp.status_code == 200
        assert models.Outcome.objects.count() == initial_outcome_count + 1
        url = reverse("epiv2:outcome-htmx", args=[outcome_2.id, "delete"])
        resp = client.post(url)
        assert resp.status_code == 200
        assert models.Outcome.objects.count() == initial_outcome_count

        # exposure level delete
        url = reverse("epiv2:exposurelevel-htmx", args=[exposure_level.id, "delete"])
        resp = client.post(url)
        assertTemplateUsed(resp, "common/fragments/_delete_rows.html")
        assert resp.status_code == 200
        assert models.ExposureLevel.objects.count() == initial_exposurelevel_count + 1
        url = reverse("epiv2:exposurelevel-htmx", args=[exposure_level_2.id, "delete"])
        resp = client.post(url)
        assert resp.status_code == 200
        assert models.ExposureLevel.objects.count() == initial_exposurelevel_count

        # exposure delete
        url = reverse("epiv2:exposure-htmx", args=[exposure.id, "delete"])
        resp = client.post(url)
        assertTemplateUsed(resp, "common/fragments/_delete_rows.html")
        assert resp.status_code == 200
        assert models.Exposure.objects.count() == initial_exposure_count + 1
        url = reverse("epiv2:exposure-htmx", args=[exposure_2.id, "delete"])
        resp = client.post(url)
        assert resp.status_code == 200
        assert models.Exposure.objects.count() == initial_exposure_count

        # chemical delete
        url = reverse("epiv2:chemical-htmx", args=[chemical.id, "delete"])
        resp = client.post(url)
        assertTemplateUsed(resp, "common/fragments/_delete_rows.html")
        assert resp.status_code == 200
        assert models.Chemical.objects.count() == initial_chem_count + 1
        url = reverse("epiv2:chemical-htmx", args=[chemical_2.id, "delete"])
        resp = client.post(url)
        assert resp.status_code == 200
        assert models.Chemical.objects.count() == initial_chem_count
