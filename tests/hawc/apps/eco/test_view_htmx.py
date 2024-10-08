import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from hawc.apps.eco import models


@pytest.mark.django_db
class TestDesignChildren:
    def test_children(self, db_keys):
        design_id = db_keys.eco_design
        design = models.Design.objects.get(id=design_id)
        client = Client(headers={"hx-request": "true"})
        assert client.login(email="pm@hawcproject.org", password="pw") is True

        init_cause_ct = models.Cause.objects.count()
        init_effect_ct = models.Effect.objects.count()
        init_result_ct = models.Result.objects.count()

        # cause create
        url = reverse("eco:cause-htmx", args=[design.id, "create"])
        term_id = models.NestedTerm.objects.first().id
        inputs = {
            "cause-new-name": "cause",
            "cause-new-term": term_id,
            "cause-new-level": "level",
            "cause-new-level_units": "grams",
            "cause-new-duration": "10 days",
            "cause-new-as_reported": "not reported",
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "eco/fragments/cause_row.html")
        assert resp.status_code == 200
        assert "<td>cause</td>" in str(resp.content)
        cause = resp.context["object"]
        assert f"cause-{cause.id}" in str(resp.content)
        assert models.Cause.objects.count() == init_cause_ct + 1

        # cause clone
        url = reverse("eco:cause-htmx", args=[cause.id, "clone"])
        resp = client.post(url)
        assertTemplateUsed(resp, "eco/fragments/cause_row.html")
        assert resp.status_code == 200
        assert "<td>cause (2)</td>" in str(resp.content)
        assert models.Cause.objects.count() == init_cause_ct + 2
        cause_2 = resp.context["object"]

        # cause read
        url = reverse("eco:cause-htmx", args=[cause.id, "read"])
        resp = client.get(url)
        assertTemplateUsed(resp, "eco/fragments/cause_row.html")
        assert resp.status_code == 200
        assert "<td>cause</td>" in str(resp.content)
        assert models.Cause.objects.count() == init_cause_ct + 2

        # cause update
        url = reverse("eco:cause-htmx", args=[cause.id, "update"])
        inputs["cause-new-name"] = "cause update"
        inputs = {k.replace("new", str(cause.id)): v for k, v in inputs.items()}
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "eco/fragments/cause_row.html")
        assert resp.status_code == 200
        assert "<td>cause update</td>" in str(resp.content)
        assert f"cause-{cause.id}" in str(resp.content)
        assert models.Cause.objects.count() == init_cause_ct + 2

        # effect create
        url = reverse("eco:effect-htmx", args=[design.id, "create"])
        inputs = {
            "effect-new-name": "effect",
            "effect-new-term": term_id,
            "effect-new-units": "grams",
            "effect-new-as_reported": "not reported",
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "eco/fragments/effect_row.html")
        assert resp.status_code == 200
        assert "<td>effect</td>" in str(resp.content)
        effect = resp.context["object"]
        assert f"effect-{effect.id}" in str(resp.content)
        assert models.Effect.objects.count() == init_effect_ct + 1

        # effect clone
        url = reverse("eco:effect-htmx", args=[effect.id, "clone"])
        resp = client.post(url)
        assertTemplateUsed(resp, "eco/fragments/effect_row.html")
        assert resp.status_code == 200
        assert "<td>effect (2)</td>" in str(resp.content)
        assert models.Effect.objects.count() == init_effect_ct + 2
        effect_2 = resp.context["object"]

        # effect read
        url = reverse("eco:effect-htmx", args=[effect.id, "read"])
        resp = client.get(url)
        assertTemplateUsed(resp, "eco/fragments/effect_row.html")
        assert resp.status_code == 200
        assert "<td>effect</td>" in str(resp.content)
        assert models.Effect.objects.count() == init_effect_ct + 2

        # effect update
        url = reverse("eco:effect-htmx", args=[effect.id, "update"])
        inputs["effect-new-name"] = "effect update"
        inputs = {k.replace("new", str(effect.id)): v for k, v in inputs.items()}
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "eco/fragments/effect_row.html")
        assert resp.status_code == 200
        assert "<td>effect update</td>" in str(resp.content)
        assert f"effect-{effect.id}" in str(resp.content)
        assert models.Effect.objects.count() == init_effect_ct + 2

        # result create
        url = reverse("eco:result-htmx", args=[design.id, "create"])
        inputs = {
            "result-new-name": "result",
            "result-new-cause": cause.id,
            "result-new-effect": effect.id,
            "result-new-sort_order": 3,
            "result-new-relationship_direction": 0,
            "result-new-modifying_factors": "none,reported",
            "result-new-variability": 94,
            "result-new-statistical_sig_type": 99,
        }
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "eco/fragments/result_row.html")
        assert resp.status_code == 200
        assert '<span class="badge badge-secondary">none</span>' in str(resp.content)
        result = resp.context["object"]
        assert f"result-{result.id}" in str(resp.content)
        assert models.Result.objects.count() == init_result_ct + 1

        # result clone
        url = reverse("eco:result-htmx", args=[result.id, "clone"])
        resp = client.post(url)
        assertTemplateUsed(resp, "eco/fragments/result_row.html")
        assert resp.status_code == 200
        assert '<span class="badge badge-secondary">none</span>' in str(resp.content)
        assert models.Result.objects.count() == init_result_ct + 2
        result_2 = resp.context["object"]

        # result read
        url = reverse("eco:result-htmx", args=[result.id, "read"])
        resp = client.get(url)
        assertTemplateUsed(resp, "eco/fragments/result_row.html")
        assert resp.status_code == 200
        assert '<span class="badge badge-secondary">none</span>' in str(resp.content)
        assert models.Result.objects.count() == init_result_ct + 2

        # result update
        url = reverse("eco:result-htmx", args=[result.id, "update"])
        inputs["result-new-modifying_factors"] = "one"
        inputs = {k.replace("new", str(result.id)): v for k, v in inputs.items()}
        resp = client.post(url, data=inputs)
        assertTemplateUsed(resp, "eco/fragments/result_row.html")
        assert resp.status_code == 200
        assert '<span class="badge badge-secondary">one</span>' in str(resp.content)
        assert f"result-{result.id}" in str(resp.content)
        assert models.Result.objects.count() == init_result_ct + 2

        # result delete
        url = reverse("eco:result-htmx", args=[result.id, "delete"])
        resp = client.post(url)
        assertTemplateUsed(resp, "common/fragments/_delete_rows.html")
        assert resp.status_code == 200
        assert models.Result.objects.count() == init_result_ct + 1
        url = reverse("eco:result-htmx", args=[result_2.id, "delete"])
        resp = client.post(url)
        assert resp.status_code == 200
        assert models.Result.objects.count() == init_result_ct

        # effect delete
        url = reverse("eco:effect-htmx", args=[effect.id, "delete"])
        resp = client.post(url)
        assertTemplateUsed(resp, "common/fragments/_delete_rows.html")
        assert resp.status_code == 200
        assert models.Effect.objects.count() == init_effect_ct + 1
        url = reverse("eco:effect-htmx", args=[effect_2.id, "delete"])
        resp = client.post(url)
        assert resp.status_code == 200
        assert models.Effect.objects.count() == init_effect_ct

        # cause delete
        url = reverse("eco:cause-htmx", args=[cause.id, "delete"])
        resp = client.post(url)
        assertTemplateUsed(resp, "common/fragments/_delete_rows.html")
        assert resp.status_code == 200
        assert models.Cause.objects.count() == init_cause_ct + 1
        url = reverse("eco:cause-htmx", args=[cause_2.id, "delete"])
        resp = client.post(url)
        assert resp.status_code == 200
        assert models.Cause.objects.count() == init_cause_ct
