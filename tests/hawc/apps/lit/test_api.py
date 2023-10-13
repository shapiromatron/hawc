import json
from io import BytesIO
from pathlib import Path

import pandas as pd
import pytest
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIClient

from hawc.apps.common.forms import ASSESSMENT_UNIQUE_MESSAGE
from hawc.apps.lit import constants, models
from hawc.apps.myuser.models import HAWCUser

from ..test_utils import check_details_of_last_log_entry, get_client

DATA_ROOT = Path(__file__).parents[3] / "data/api"


@pytest.mark.django_db
class TestLiteratureAssessmentViewSet:
    def _test_flat_export(
        self, rewrite_data_files: bool, fn: str, url: str, client: APIClient | None = None
    ):
        if client is None:
            client = APIClient()
            assert client.login(username="reviewer@hawcproject.org", password="pw") is True

        resp = client.get(url)
        assert resp.status_code == 200

        path = Path(DATA_ROOT / fn)
        data = resp.json()

        if rewrite_data_files:
            path.write_text(json.dumps(data, indent=2, sort_keys=True))

        assert data == json.loads(path.read_text())

    def test_permissions(self, db_keys):
        rev_client = APIClient()
        assert rev_client.login(username="reviewer@hawcproject.org", password="pw") is True
        anon_client = APIClient()
        pm_client = APIClient()
        assert pm_client.login(username="pm@hawcproject.org", password="pw") is True

        urls = [
            reverse("lit:api:assessment-tags", args=(db_keys.assessment_working,)),
            reverse("lit:api:assessment-reference-ids", args=(db_keys.assessment_working,)),
            reverse("lit:api:assessment-reference-tags", args=(db_keys.assessment_working,)),
            reverse(
                "lit:api:assessment-reference-year-histogram", args=(db_keys.assessment_working,)
            ),
            reverse("lit:api:assessment-reference-export", args=(db_keys.assessment_working,)),
            reverse("lit:api:assessment-tag-heatmap", args=(db_keys.assessment_working,)),
            reverse("lit:api:assessment-tagtree", args=(db_keys.assessment_working,)),
        ]
        for url in urls:
            assert anon_client.get(url).status_code == 403
            assert rev_client.get(url).status_code == 200

        # user-tag data
        for url in [
            reverse("lit:api:assessment-user-tag-export", args=(db_keys.assessment_final,)),
        ]:
            assert anon_client.get(url).status_code == 403
            assert rev_client.get(url).status_code == 403
            assert pm_client.get(url).status_code == 200

        # only admins and up can POST
        url = reverse("lit:api:assessment-tagtree", args=(db_keys.assessment_working,))
        assert anon_client.post(url).status_code == 403
        assert rev_client.post(url).status_code == 403
        assert pm_client.post(url, None).status_code == 400  # validation; not permission error

    def test_export(self, rewrite_data_files: bool, db_keys):
        url = reverse("lit:api:assessment-reference-export", args=(db_keys.assessment_final,))
        fn = "api-lit-assessment-reference-export.json"
        self._test_flat_export(rewrite_data_files, fn, url)

    def test_references_export_format(self, db_keys):
        url = reverse("lit:api:assessment-reference-export", args=(db_keys.assessment_final,))
        c = APIClient()
        assert c.login(email="team@hawcproject.org", password="pw") is True

        # base report; reference metadata plus columns for each tag
        resp = c.get(url, {"tag": 12}).json()
        assert len(resp) == 2
        assert len(resp[0]) > 20
        assert resp[0]["Inclusion"] is True

        # table builder format
        resp = c.get(url, {"tag": 12, "export_format": "table-builder"}).json()
        assert len(resp) == 2
        assert len(resp[0]) == 5
        assert resp[0]["Name"] == "Kawana N, Ishimatsu S, and Kanda K 2001"

    def test_export_user_tags(self, rewrite_data_files: bool, db_keys):
        pm_client = APIClient()
        assert pm_client.login(username="pm@hawcproject.org", password="pw") is True
        url = reverse(
            "lit:api:assessment-user-tag-export", args=(db_keys.assessment_conflict_resolution,)
        )
        fn = "api-lit-assessment-reference-export-user-tags.json"
        self._test_flat_export(rewrite_data_files, fn, url, pm_client)

    def test_tags(self, db_keys):
        url = reverse("lit:api:assessment-tags", kwargs=dict(pk=db_keys.assessment_working))
        c = APIClient()
        assert c.login(email="pm@hawcproject.org", password="pw") is True
        resp = c.get(url).json()
        assert len(resp) == 11
        assert resp[0] == {"id": 2, "depth": 2, "name": "Inclusion", "nested_name": "Inclusion"}
        assert resp[-1] == {
            "id": 21,
            "depth": 4,
            "name": "c",
            "nested_name": "Exclusion|Tier III|c",
        }

    def test_tagtree(self, db_keys):
        url = reverse("lit:api:assessment-tagtree", kwargs=dict(pk=db_keys.assessment_working))
        c = APIClient()

        # test some updates
        bad_payload_no_name = {
            "tree": [{"data": {"name": "x"}}, {"data": {"name": "y"}, "children": [{"data": {}}]}]
        }
        bad_payload_bad_slug = {"tree": [{"data": {"name": "x", "slug": "this has spaces"}}]}

        good_payload = {
            "tree": [
                {"data": {"name": "This is required"}},
                {"data": {"name": "Tag Name", "slug": "custom-slug"}},
                {
                    "data": {"name": "Grandparent Tag"},
                    "children": [
                        {"data": {"name": "nested"}},
                        {
                            "data": {"name": "Parent Tag"},
                            "children": [{"data": {"name": "deeply nested"}}],
                        },
                    ],
                },
            ]
        }

        # permissions - GET/POST
        assert c.login(email="reviewer@hawcproject.org", password="pw") is True
        response = c.get(url)
        assert response.status_code == 200
        response = c.post(url, good_payload, format="json")
        assert response.status_code == 403

        # test some basic fetching
        assert c.login(email="pm@hawcproject.org", password="pw") is True
        resp = c.get(url).json()["tree"]
        assert len(resp) == 2
        assert len(resp[0]["children"]) == 3
        assert resp[1]["data"]["name"] == "Exclusion"
        assert resp[0]["children"][2]["data"]["slug"] == "mechanistic-study"

        # bad input - no data supplied
        response = c.post(url, None, format="json")
        assert response.status_code == 400
        assert response.json() == {"tree": ["This field is required."]}

        # bad input - it's JSON but not a list as we expect
        response = c.post(url, {}, format="json")
        assert response.status_code == 400
        assert response.json() == {"tree": ["This field is required."]}

        # bad input - what if the "name" attribute is missing from a node
        response = c.post(url, bad_payload_no_name, format="json")
        error = response.json()
        assert response.status_code == 400
        assert "'name' is a required property" in error["tree"][0]

        # bad input - a slug is supplied but it's not valid
        response = c.post(url, bad_payload_bad_slug, format="json")
        error = response.json()
        assert response.status_code == 400
        assert "does not match" in error["tree"][0]

        # good payload
        response = c.post(url, good_payload, format="json")
        assert response.status_code == 200
        check_details_of_last_log_entry(db_keys.assessment_working, "Updated (tagtree replace)")
        data = response.json()["tree"]
        assert data[0]["id"] > 0
        assert data[0]["data"]["name"] == "This is required"
        assert data[0]["data"]["slug"] == "this-is-required"
        assert data[1]["data"]["name"] == "Tag Name"
        assert data[1]["data"]["slug"] == "custom-slug"
        assert data[2]["children"][0]["data"]["name"] == "nested"

    def test_reference_ids(self, db_keys):
        # create new reference w/ no external identifiers; should also be included
        models.Reference.objects.create(id=9999, assessment_id=db_keys.assessment_final)
        url = reverse("lit:api:assessment-reference-ids", kwargs=dict(pk=db_keys.assessment_final))
        c = APIClient()
        assert c.login(email="pm@hawcproject.org", password="pw") is True
        resp = c.get(url).json()
        assert resp == [
            {
                "reference_id": 5,
                "pubmed_id": 11778423,
                "hero_id": None,
                "doi": "10.1093/milmed/166.suppl_2.23",
            },
            {"reference_id": 6, "pubmed_id": 15907334, "hero_id": None, "doi": None},
            {"reference_id": 7, "pubmed_id": 21284075, "hero_id": None, "doi": None},
            {"reference_id": 8, "pubmed_id": 24004895, "hero_id": None, "doi": None},
            {"reference_id": 12, "pubmed_id": 28572920.0, "hero_id": None, "doi": None},
            {"reference_id": 9999, "pubmed_id": None, "hero_id": None, "doi": None},
        ]

    def test_reference_tags(self, db_keys):
        url = reverse("lit:api:assessment-reference-tags", kwargs=dict(pk=db_keys.assessment_final))
        c = APIClient()
        assert c.login(email="pm@hawcproject.org", password="pw") is True
        resp = c.get(url).json()
        assert resp == [
            {"reference_id": 5, "tag_id": 12},
            {"reference_id": 6, "tag_id": 13},
            {"reference_id": 7, "tag_id": 13},
            {"reference_id": 8, "tag_id": 12},
        ]

    def test_reference_year_histogram(self, db_keys):
        url = reverse(
            "lit:api:assessment-reference-year-histogram",
            kwargs=dict(pk=db_keys.assessment_working),
        )
        c = APIClient()
        assert c.login(email="pm@hawcproject.org", password="pw") is True
        resp = c.get(url).json()
        assert resp["data"][0]["type"] == "histogram"

    def test_tag_heatmap(self, rewrite_data_files: bool, db_keys):
        url = reverse("lit:api:assessment-tag-heatmap", args=(db_keys.assessment_final,))
        fn = "api-lit-assessment-tag-heatmap.json"
        self._test_flat_export(rewrite_data_files, fn, url)

    def test_excel_to_json(self, db_keys):
        url = reverse("lit:api:assessment-excel-to-json", args=(db_keys.assessment_working,))
        data = [{"reference_id": 1, "tag_id": 1}, {"reference_id": 1, "tag_id": 2}]
        df = pd.DataFrame(data)
        excel = BytesIO()
        df.to_excel(excel, index=False)
        excel.seek(0)
        csv = BytesIO(df.to_csv(index=False).encode())
        csv.seek(0)
        c = APIClient()

        # permission error
        disposition = "attachment; filename=test.xlsx"
        resp = c.post(url, {"file": csv}, HTTP_CONTENT_DISPOSITION=disposition)
        assert resp.status_code == 403

        assert c.login(email="pm@hawcproject.org", password="pw") is True

        # valid; assert parses successfully
        disposition = "attachment; filename=test.xlsx"
        resp = c.post(url, {"file": excel}, HTTP_CONTENT_DISPOSITION=disposition)
        assert resp.status_code == 200 and resp.json() == data

        # invalid; JSON with no file
        resp = c.post(url, {"test": 123}, format="json")
        assert resp.status_code == 400 and resp.json() == {
            "detail": "Missing filename. Request should include a Content-Disposition header with a filename parameter."
        }

        # invalid; Content-Disposition header is required
        resp = c.post(url, {"file": excel})
        assert resp.status_code == 400 and resp.json() == {
            "detail": "Missing filename. Request should include a Content-Disposition header with a filename parameter."
        }

        # invalid; no file returns an error
        resp = c.post(url)
        assert resp.status_code == 400 and resp.json() == {"file": "A file is required"}

        # invalid; non excel files return an error
        resp = c.post(url, {"file": csv}, HTTP_CONTENT_DISPOSITION="attachment; filename=test.csv")
        assert resp.status_code == 400 and resp.json() == {"file": "File extension must be .xlsx"}

        # invalid; cannot parse excel file
        resp = c.post(url, {"file": BytesIO()}, HTTP_CONTENT_DISPOSITION=disposition)
        assert resp.status_code == 400 and resp.json() == {"file": "Unable to parse excel file"}
        resp = c.post(url, {"file": csv}, HTTP_CONTENT_DISPOSITION=disposition)
        assert resp.status_code == 400 and resp.json() == {"file": "Unable to parse excel file"}


@pytest.mark.vcr
@pytest.mark.django_db
class TestSearchViewSet:
    def test_success(self, db_keys):
        url = reverse("lit:api:search-list")
        c = APIClient()
        assert c.login(email="team@hawcproject.org", password="pw") is True

        # HERO import
        payload = {
            "assessment": db_keys.assessment_working,
            "search_type": "i",
            "source": 2,
            "title": "demo title",
            "description": "",
            "search_string": "5490558",
        }
        resp = c.post(url, payload, format="json")
        assert resp.status_code == 201

        # PubMed import
        payload = {
            "assessment": db_keys.assessment_working,
            "search_type": "i",
            "source": 1,
            "title": "demo title 1",
            "description": "",
            "search_string": "19425233",
        }
        resp = c.post(url, payload, format="json")
        assert resp.status_code == 201

        # search string with duplicates
        payload.update(search_string="5490558, 5490558", title="second demo")
        resp = c.post(url, payload, format="json")
        assert resp.status_code == 201

    def test_validation_failures(self, db_keys):
        url = reverse("lit:api:search-list")
        c = APIClient()
        assert c.login(email="team@hawcproject.org", password="pw") is True

        # check that the "GET" method is disabled
        assert c.get(url).status_code == 405

        payload = {
            "assessment": db_keys.assessment_working,
            "search_type": "i",
            "source": 2,
            "title": "demo title",
            "description": "",
            "search_string": "5490558",
        }

        # check invalid assessment permission
        new_payload = {**payload, **{"assessment": db_keys.assessment_final}}
        resp = c.post(url, new_payload, format="json")
        assert resp.status_code == 403
        assert resp.data == {"detail": "Invalid permissions to edit assessment"}

        # title already exists for this assessment
        new_payload = {**payload, **{"title": "Manual import"}}
        resp = c.post(url, new_payload, format="json")
        assert resp.status_code == 400
        assert resp.data == {
            "non_field_errors": ["The fields assessment, title must make a unique set."]
        }

        # slug already exists for this assessment
        new_payload = {**payload, **{"title": "MANUAL IMPORT"}}
        resp = c.post(url, new_payload, format="json")
        assert resp.status_code == 400
        assert resp.data == {"slug": [ASSESSMENT_UNIQUE_MESSAGE]}

        # check type
        new_payload = {**payload, **{"search_type": "s"}}
        resp = c.post(url, new_payload, format="json")
        assert resp.status_code == 400
        assert resp.data == {"non_field_errors": ["API currently only supports imports"]}

        # check database
        new_payload = {**payload, **{"source": 3}}
        resp = c.post(url, new_payload, format="json")
        assert resp.status_code == 400
        assert resp.data == {
            "non_field_errors": ["API currently only supports PubMed/HERO imports"]
        }

        # check bad csv
        bad_search_strings = [
            "",
            "just a long string of text",
            "not-numeric,but a csv",
            "1a,2b",
            "1,,2",
            "1,2, ,3",
        ]
        for bad_search_string in bad_search_strings:
            new_payload = {**payload, **{"search_string": bad_search_string}}
            resp = c.post(url, new_payload, format="json")
            assert resp.status_code == 400
            assert resp.data == {
                "non_field_errors": [
                    "Must be a comma-separated list of positive integer identifiers"
                ]
            }

        # check bad id lists
        bad_search_strings = ["-1"]
        for bad_search_string in bad_search_strings:
            new_payload = {**payload, **{"search_string": bad_search_string}}
            resp = c.post(url, new_payload, format="json")
            assert resp.status_code == 400
            assert resp.data == {
                "non_field_errors": ["At least one positive identifier must exist"]
            }

    def test_missing_id_in_hero(self, db_keys):
        """
        This should fail b/c the ID is redirected in HERO (search for HERO ID 41589):
        - https://hero.epa.gov/hero/index.cfm/search
        - https://hero.epa.gov/hero/index.cfm/reference/details/reference_id/5490558

        This is an empty return:
        - https://hero.epa.gov/hero/ws/index.cfm/api/1.0/search/criteria/41589/recordsperpage/100
        """
        url = reverse("lit:api:search-list")
        c = APIClient()
        assert c.login(email="team@hawcproject.org", password="pw") is True

        # check missing id
        payload = {
            "assessment": db_keys.assessment_working,
            "search_type": "i",
            "source": 2,
            "title": "demo title 2",
            "description": "",
            "search_string": "41589",
        }
        resp = c.post(url, payload, format="json")
        assert resp.status_code == 400
        assert resp.data == {
            "non_field_errors": ["The following HERO ID(s) could not be imported: 41589"]
        }


@pytest.mark.vcr
@pytest.mark.django_db
class TestHEROApis:
    @pytest.fixture(scope="function", autouse=True)
    def clear_cache(cls):
        # Reset burst throttling
        cache.clear()

    def test_replace_permissions(self, db_keys):
        assessment_id = models.Reference.objects.get(id=db_keys.reference_linked).assessment_id

        url = reverse("lit:api:assessment-replace-hero", args=(assessment_id,))
        data = {"replace": [[db_keys.reference_linked, 1]]}

        # reviewers shouldn't be able to update
        client = APIClient()
        assert client.login(username="reviewer@hawcproject.org", password="pw") is True
        response = client.post(url, data, format="json")
        assert response.status_code == 403

        # public shouldn't be able to update
        client = APIClient()
        response = client.post(url, data, format="json")
        assert response.status_code == 403

    def test_valid_replace_requests(self, db_keys):
        assessment_id = models.Reference.objects.get(id=db_keys.reference_linked).assessment_id

        url = reverse("lit:api:assessment-replace-hero", args=(assessment_id,))
        data = {"replace": [[db_keys.reference_linked, 1]]}

        client = APIClient()
        assert client.login(username="pm@hawcproject.org", password="pw") is True
        response = client.post(url, data, format="json")
        assert response.status_code == 204
        check_details_of_last_log_entry(assessment_id, "Updated (HERO replacements)")

        updated_reference = models.Reference.objects.get(id=db_keys.reference_linked)
        assert (
            updated_reference.title
            == "Asbestos-related diseases of the lungs and pleura: Current clinical issues"
        )
        assert updated_reference.identifiers.get(
            database=constants.ReferenceDatabase.HERO
        ).unique_id == str(1)

    def test_bad_replace_requests(self, db_keys):
        # test nonexistent assessment
        url = reverse("lit:api:assessment-replace-hero", args=(100,))
        data = {"replace": [[db_keys.reference_linked, 1]]}

        client = APIClient()
        assert client.login(username="pm@hawcproject.org", password="pw") is True
        response = client.post(url, data, format="json")
        assert response.status_code == 404

    def test_update_permissions(self, db_keys):
        assessment_id = models.Reference.objects.get(id=db_keys.reference_linked).assessment_id

        url = reverse(
            "lit:api:assessment-update-reference-metadata-from-hero", args=(assessment_id,)
        )

        # reviewers shouldn't be able to destroy
        client = APIClient()
        assert client.login(username="reviewer@hawcproject.org", password="pw") is True
        response = client.post(url)
        assert response.status_code == 403

        # public shouldn't be able to update
        client = APIClient()
        response = client.post(url)
        assert response.status_code == 403

    def test_valid_update_requests(self, db_keys):
        assessment_id = models.Reference.objects.get(id=db_keys.reference_linked).assessment_id

        url = reverse(
            "lit:api:assessment-update-reference-metadata-from-hero", args=(assessment_id,)
        )

        client = APIClient()
        assert client.login(username="pm@hawcproject.org", password="pw") is True
        response = client.post(url)
        assert response.status_code == 204
        check_details_of_last_log_entry(assessment_id, "Updated (HERO metadata)")

        updated_reference = models.Reference.objects.get(id=db_keys.reference_linked)
        assert updated_reference.title == "Early lung events following low-dose asbestos exposure"

    def test_bad_update_requests(self, db_keys):
        # test nonexistent assessment
        url = reverse("lit:api:assessment-replace-hero", args=(100,))

        client = APIClient()
        assert client.login(username="pm@hawcproject.org", password="pw") is True
        response = client.post(url)
        assert response.status_code == 404


@pytest.mark.django_db
class TestReferenceDestroyApi:
    def test_permissions(self, db_keys):
        url = reverse("lit:api:reference-detail", args=(db_keys.reference_linked,))

        # reviewers shouldn't be able to destroy
        client = APIClient()
        assert client.login(username="reviewer@hawcproject.org", password="pw") is True
        response = client.delete(url)
        assert response.status_code == 403

        # public shouldn't be able to destroy
        client = APIClient()
        response = client.delete(url)
        assert response.status_code == 403

        # make sure the object still exists
        assert models.Reference.objects.filter(id=db_keys.reference_linked).exists()

    def test_bad_requests(self, db_keys):
        # test bad id
        url = reverse("lit:api:reference-detail", args=(-1,))

        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True
        response = client.delete(url)
        assert response.status_code == 404

    def test_valid_requests(self, db_keys):
        # test valid id
        url = reverse("lit:api:reference-detail", args=(db_keys.reference_linked,))

        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True
        response = client.delete(url)
        # the reference is successfully deleted
        assert response.status_code == 204
        response = client.delete(url)
        # the object does not exist, since it was previously deleted
        assert response.status_code == 404
        assert not models.Reference.objects.filter(id=db_keys.reference_linked).exists()


@pytest.mark.django_db
class TestReferenceViewSet:
    def test_update_permissions(self, db_keys):
        url = reverse("lit:api:reference-detail", args=(db_keys.reference_linked,))
        data = {"title": "TestReferenceUpdateApi test"}

        pre_ref = models.Reference.objects.get(id=db_keys.reference_linked)

        # reviewers shouldn't be able to update
        client = APIClient()
        assert client.login(username="reviewer@hawcproject.org", password="pw") is True

        response = client.patch(url, data)
        assert response.status_code == 403

        # public shouldn't be able to update
        client = APIClient()
        response = client.patch(url, data)
        assert response.status_code == 403

        post_ref = models.Reference.objects.get(id=db_keys.reference_linked)

        # make sure the object hasn't changed
        assert post_ref == pre_ref

    def test_update_bad_requests(self, db_keys):
        # test bad id
        url = reverse("lit:api:reference-detail", args=(-1,))
        data = {"title": "TestReferenceUpdateApi test"}

        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True
        response = client.patch(url, data)
        assert response.status_code == 404

        # test bad tag
        url = reverse("lit:api:reference-detail", args=(db_keys.reference_linked,))
        tags = [2, 3, -1]
        data = {"tags": tags}
        response = client.patch(url, data)
        assert response.status_code == 400
        assert response.json() == {"tags": ["All tag ids are not from this assessment"]}

    def test_update_valid_requests(self, db_keys):
        url = reverse("lit:api:reference-detail", args=(db_keys.reference_linked,))
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        reference = models.Reference.objects.get(id=db_keys.reference_linked)

        # test updating reference with a new title
        data = {"title": "TestReferenceUpdateApi title test"}
        response = client.patch(url, data)
        assert response.status_code == 200

        assert reference.title != data.get("title")
        updated_reference = models.Reference.objects.get(id=db_keys.reference_linked)
        assert updated_reference.title == data.get("title")

        # test updating reference with new tags
        tags = [2, 3]
        data = {"tags": tags}
        response = client.patch(url, data)
        assert response.status_code == 200

        updated_reference = models.Reference.objects.get(id=db_keys.reference_linked)
        assert updated_reference.tags.count() == len(tags)
        for id in tags:
            assert updated_reference.tags.filter(id=id).exists()

        # test updating reference with multiple fields
        tags = [2, 3, 4]
        data = {"title": "TestReferenceUpdateApi title test 2", "tags": tags}
        response = client.patch(url, data)
        assert response.status_code == 200

        updated_reference = models.Reference.objects.get(id=db_keys.reference_linked)
        assert updated_reference.title == data.get("title")
        assert updated_reference.tags.count() == len(tags)
        for id in tags:
            assert updated_reference.tags.filter(id=id).exists()

    def test_tag_permissions(self, db_keys):
        ref: models.Reference = models.Reference.objects.get(id=db_keys.reference_tag_conflict)
        update_tags_url = reverse("lit:api:reference-tag", args=(ref.pk,))
        resolve_conflict_url = reverse("lit:api:reference-resolve-conflict", args=(ref.pk,))

        assert ref.tags.count() == 0
        assert ref.user_tags.count() == 2
        assert ref.user_tags.filter(user__email="reviewer@hawcproject.org").exists() is False
        assert ref.has_user_tag_conflicts() is True

        # reviewers can't update tags or resolve conflicts
        client = APIClient()
        assert client.login(username="reviewer@hawcproject.org", password="pw") is True
        response = client.post(update_tags_url, data={"tags": [32, 33]}, format="json")
        assert response.status_code == 403

        # no user tag was created
        ref.refresh_from_db()
        assert ref.user_tags.count() == 2
        assert ref.user_tags.filter(user__email="reviewer@hawcproject.org").exists() is False

        user_tag_id = ref.user_tags.first().pk
        response = client.post(resolve_conflict_url, data={"user_tag_id": user_tag_id})
        assert response.status_code == 403

        # tags were not added to the reference/conflict was not resolved
        ref.refresh_from_db()
        assert ref.tags.count() == 0
        assert ref.has_user_tag_conflicts() is True

    def test_conflict_valid(self, db_keys):
        ref: models.Reference = models.Reference.objects.get(id=db_keys.reference_untagged)
        pm = HAWCUser.objects.get(email="pm@hawcproject.org")
        tm = HAWCUser.objects.get(email="team@hawcproject.org")

        pm_tags = [32]
        tm_tags = [33]

        update_tags_url = reverse("lit:api:reference-tag", args=(ref.pk,))
        resolve_conflict_url = reverse("lit:api:reference-resolve-conflict", args=(ref.pk,))

        client = APIClient()

        assert ref.user_tags.count() == 0
        assert ref.has_user_tag_conflicts() is False

        # create a conflict by applying different tags as two different users
        assert client.login(email=tm.email, password="pw") is True
        response = client.post(update_tags_url, data={"tags": tm_tags}, format="json")
        assert response.status_code == 200
        client.logout()

        assert client.login(email=pm.email, password="pw") is True
        response = client.post(update_tags_url, data={"tags": pm_tags}, format="json")
        assert response.status_code == 200

        ref.refresh_from_db()
        assert ref.user_tags.count() == 2
        assert ref.has_user_tag_conflicts() is True
        assert ref.tags.count() == 0

        # resolve the conflict using Project Manager's tags
        pm_user_tag = ref.user_tags.get(user=pm)
        response = client.post(resolve_conflict_url, data={"user_tag_id": pm_user_tag.pk})
        assert response.status_code == 200

        ref.refresh_from_db()
        assert ref.has_user_tag_conflicts() is False
        assert list(ref.tags.values_list("id", flat=True)) == pm_tags

    def test_tagging_valid(self, db_keys):
        ref: models.Reference = models.Reference.objects.get(id=db_keys.reference_untagged)
        client = APIClient()
        assert client.login(email="pm@hawcproject.org", password="pw") is True

        # test applying tags w/o conflict resolution
        ref = models.Reference.objects.get(id=db_keys.reference_linked)
        update_tags_url = reverse("lit:api:reference-tag", args=(ref.pk,))
        tags = [2, 3]
        response = client.post(update_tags_url, data={"tags": tags}, format="json")
        assert response.status_code == 200

        # tags are applied to the reference without creating a conflict
        ref.refresh_from_db()
        assert list(ref.tags.values_list("id", flat=True)) == tags
        assert ref.has_user_tag_conflicts() is False

    def test_tagging_invalid(self, db_keys):
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True
        url = reverse("lit:api:reference-tag", args=(-1,))

        # test bad id
        data = {"tags": [2, 3]}
        response = client.post(url, data, format="json")
        assert response.status_code == 404

        # test bad tag
        url = reverse("lit:api:reference-tag", args=(db_keys.reference_linked,))
        data = {"tags": [2, 3, -1]}
        response = client.post(url, data, format="json")
        assert response.status_code == 400
        assert response.json() == {"tags": "Array of tags must be valid primary keys"}

    def test_merge_tag_permissions(self):
        team = get_client("team", api=True)
        reviewer = get_client("reviewer", api=True)
        url = reverse("lit:api:reference-merge-tags", args=[11])

        response = reviewer.post(url)
        assert response.status_code == 403

        response = team.post(url)
        assert response.status_code == 200

    def test_conflict_invalid(self, db_keys):
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True
        url = reverse("lit:api:reference-resolve-conflict", args=(-1,))

        # test bad ref id
        data = {"user_tag_id": 1}
        response = client.post(url, data, format="json")
        assert response.status_code == 404

        # test bad user_tag_id (wrong reference)
        url = reverse("lit:api:reference-resolve-conflict", args=(db_keys.reference_tag_conflict,))
        data = {"user_tag_id": 1}
        response = client.post(url, data, format="json")
        assert response.status_code == 404

        # test bad user_tag_id (doesn't exist)
        data = {"user_tag_id": -1}
        response = client.post(url, data, format="json")
        assert response.status_code == 404

    def test_id_search(self):
        client = APIClient()
        url = reverse(
            "lit:api:reference-id-search", args=[constants.ReferenceDatabase.PUBMED, 15907334]
        )

        assert client.login(username="pm@hawcproject.org", password="pw") is True
        response = client.get(url)
        assert response.status_code == 403

        assert client.login(username="admin@hawcproject.org", password="pw") is True
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.json()) == 1
