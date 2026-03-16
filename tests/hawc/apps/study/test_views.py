import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from hawc.apps.lit.models import Reference
from hawc.apps.study.models import Attachment

from ..test_utils import check_200, check_302, check_403, get_client


@pytest.mark.django_db
class TestStudyCreateFromReference:
    def test_redirect(self):
        client = get_client("team")
        url = reverse("study:new_study", args=(1,))
        check_302(client, url, reverse("study:detail", args=(1,)))

    def test_success(self):
        ref = Reference.objects.create(assessment_id=1)
        client = get_client("team")

        url = reverse("study:new_study", args=(ref.id,))
        resp = client.post(url, {"short_citation": "test", "full_citation": "a", "coi_reported": 0})
        assert resp.status_code == 302
        assert resp.url == reverse("study:detail", args=(ref.id,))


@pytest.mark.django_db
class TestCloneViewSet:
    def test_get(self):
        team = get_client("team")
        dst_assesment = 1
        url = reverse("study:clone_from_assessment", args=(dst_assesment,))
        resp = check_200(team, url)
        assertTemplateUsed(resp, "study/study_clone.html")

    def test_post_fetch(self):
        team = get_client("team", htmx=True)
        dst_assesment = 1
        url = reverse("study:clone_from_assessment", args=(dst_assesment,))
        resp = team.post(url, {"action": "fetch", "src_assessment": 2})
        assert resp.status_code == 200
        assertTemplateUsed(resp, "study/fragments/clone_fetch.html")

    def test_bad_post_actions(self):
        team = get_client("team", htmx=True)
        dst_assesment = 1
        url = reverse("study:clone_from_assessment", args=(dst_assesment,))

        # bad src assessment
        resp = team.post(url, {"action": "fetch", "src_assessment": 9999})
        assert resp.status_code == 400

        # bad actions
        resp = team.post(url, {"src_assessment": 2})
        assert resp.status_code == 400
        resp = team.post(url, {"action": "zzz", "src_assessment": 2})
        assert resp.status_code == 400

    def _valid_clone_payload(self):
        return {
            "action": "clone",
            "src_assessment": 2,
            "study": [7],
            "study_bioassay": [7],
            "study_epi": [],
            "study_rob": [7],
            "include_rob": True,
            "copy_mode": "final-to-final",
            "metric-1": 14,
            "metric-2": 15,
        }

    def test_post_clone(self):
        team = get_client("team", htmx=True)
        dst_assesment = 1
        url = reverse("study:clone_from_assessment", args=(dst_assesment,))
        resp = team.post(url, self._valid_clone_payload())
        assert resp.status_code == 200
        assertTemplateUsed(resp, "study/fragments/clone_success.html")

    def test_post_clone_errors(self):
        team = get_client("team", htmx=True)
        dst_assesment = 1
        url = reverse("study:clone_from_assessment", args=(dst_assesment,))

        # bad src ID
        data = self._valid_clone_payload()
        data["metric-1"] = 9999
        resp = team.post(url, data)
        assert resp.status_code == 200
        assertTemplateUsed(resp, "study/fragments/clone_failure.html")

        # bad destination ID
        data = self._valid_clone_payload()
        data["metric-9999"] = data["metric-1"]
        resp = team.post(url, data)
        assert resp.status_code == 200
        assertTemplateUsed(resp, "study/fragments/clone_failure.html")


@pytest.mark.django_db
def test_study_read_success(db_keys):
    clients = [
        ("admin@hawcproject.org", (200, 200, 200, 200)),
        ("pm@hawcproject.org", (200, 200, 200, 200)),
        ("team@hawcproject.org", (200, 200, 200, 200)),
        ("reviewer@hawcproject.org", (200, 403, 200, 200)),
    ]
    views = [
        reverse("study:list", kwargs={"pk": db_keys.assessment_working}),
        reverse("study:detail", kwargs={"pk": db_keys.study_working}),
        reverse("study:list", kwargs={"pk": db_keys.assessment_final}),
        reverse("study:detail", kwargs={"pk": db_keys.study_final_bioassay}),
    ]

    for client, codes in clients:
        c = Client()
        assert c.login(username=client, password="pw") is True
        for view, code in zip(views, codes, strict=True):
            response = c.get(view)
            assert response.status_code == code


@pytest.mark.django_db
def test_study_read_failure(db_keys):
    # anonymous user
    c = Client()
    views = [
        {"view": reverse("study:list", kwargs={"pk": db_keys.assessment_working}), "status": 403},
        {"view": reverse("study:detail", kwargs={"pk": db_keys.study_working}), "status": 403},
        {"view": reverse("study:list", kwargs={"pk": db_keys.assessment_final}), "status": 200},
        {
            "view": reverse("study:detail", kwargs={"pk": db_keys.study_final_bioassay}),
            "status": 200,
        },
    ]
    for view in views:
        response = c.get(view["view"])
        assert response.status_code == view["status"]


@pytest.mark.django_db
def test_study_crud_success(db_keys):
    # Check to ensure that sudo, pm and team have CRUD permissions.
    # Create a new study, edit, view prior versions, and delete. Test both
    # GET and POST when appropriate.
    clients = ["admin@hawcproject.org", "pm@hawcproject.org", "team@hawcproject.org"]
    for client in clients:
        c = Client()
        assert c.login(username=client, password="pw") is True

        # create new
        response = c.get(reverse("study:new_ref", kwargs={"pk": db_keys.assessment_working}))
        assert response.status_code == 200

        with assertTemplateUsed("study/study_detail.html"):
            response = c.post(
                reverse("study:new_ref", kwargs={"pk": db_keys.assessment_working}),
                {
                    "assessment": db_keys.assessment_working,
                    "short_citation": "foo et al.",
                    "full_citation": "cite",
                    "bioassay": True,
                    "coi_reported": 0,
                },
                follow=True,
            )

        assert response.status_code == 200
        pk = response.context["object"].id

        # edit
        response = c.get(reverse("study:update", args=(pk,)))
        assert response.status_code == 200

        with assertTemplateUsed("study/study_detail.html"):
            response = c.post(
                reverse("study:update", args=(pk,)),
                {
                    "assessment": db_keys.assessment_working,
                    "short_citation": "foo et al.",
                    "full_citation": "cite",
                    "coi_reported": 0,
                },
                follow=True,
            )
            assert response.status_code == 200

        # delete
        response = c.get(reverse("study:delete", args=(pk,)))
        assertTemplateUsed(response, "study/study_confirm_delete.html")
        assert response.status_code == 200

        response = c.post(reverse("study:delete", args=(pk,)), follow=True)
        assertTemplateUsed(response, "study/study_list.html")
        assert response.status_code == 200


@pytest.mark.django_db
def test_uf_crud_failure(db_keys):
    # Check to ensure that rev and None don't have CRUD permissions.
    # Attempt to create a new study, edit, view prior versions, and delete.
    # Test both GET and POST when appropriate.

    # first test working scenario
    users = ["reviewer@hawcproject.org", None]
    views = [
        reverse("study:new_ref", kwargs={"pk": db_keys.assessment_working}),
        reverse("study:update", kwargs={"pk": db_keys.study_working}),
        reverse("study:delete", kwargs={"pk": db_keys.study_working}),
    ]

    for user in users:
        c = Client()
        if user:
            assert c.login(username=user, password="pw") is True

        for view in views:
            response = c.get(view)
            assert response.status_code == 403
            response = c.post(view)
            assert response.status_code in [403, 405]

    # next check that all people (except sudo) cannot edit a final study
    users = ["pm@hawcproject.org", "team@hawcproject.org", "reviewer@hawcproject.org", None]
    views = [
        reverse("study:new_ref", kwargs={"pk": db_keys.assessment_final}),
        reverse("study:update", kwargs={"pk": db_keys.study_final_bioassay}),
        reverse("study:delete", kwargs={"pk": db_keys.study_final_bioassay}),
    ]

    for user in users:
        c = Client()
        if user:
            assert c.login(username=user, password="pw") is True

        for view in views:
            response = c.get(view)
            assert response.status_code == 403
            response = c.post(view)
            assert response.status_code in [403, 405]


@pytest.mark.django_db
def test_get_200():
    client = get_client("pm")
    main = 1

    url_redirect = reverse("study:rob_redirect", args=(main,))
    assert client.get(url_redirect).status_code == 301
    url_toggle_lock = reverse("study:toggle-lock", args=(main,))
    assert client.get(url_toggle_lock).status_code == 302

    urls = [
        reverse("study:new_ref", args=(main,)),
        reverse("study:create_from_identifier", args=(main,)),
        reverse("study:attachment_create", args=(main,)),
        reverse("study:list", args=(main,)),
        reverse("study:detail", args=(main,)),
        reverse("study:delete", args=(main,)),
        reverse("study:new_study", args=(3,)),
    ]
    for url in urls:
        check_200(client, url)


@pytest.mark.django_db
class TestAttachmentCrud:
    def test_create_read_delete(self):
        study_id = 1
        anon = get_client()
        client = get_client("team")
        study_url = reverse("study:detail", args=(study_id,))

        # create attachment
        assert Attachment.objects.filter(study_id=study_id).exists() is False
        url = reverse("study:attachment_create", args=(study_id,))
        resp = client.post(url, {"attachment": SimpleUploadedFile("z.txt", b"test")})
        assert resp.url == study_url
        attachment = Attachment.objects.get(study_id=study_id)

        # detail - check team member can view
        url = attachment.get_absolute_url()
        resp = client.get(url)
        check_302(client, url, attachment.attachment.url)

        # detail - check anonymous cannot view
        check_403(anon, url)

        # delete attachment
        url = attachment.get_delete_url()
        check_200(client, url)
        resp = client.post(url)
        assert resp.status_code == 302
        assert resp.url == study_url
        assert Attachment.objects.filter(study_id=study_id).exists() is False

        # cleanup (delete attachment)
        attachment.attachment.delete(save=False)
