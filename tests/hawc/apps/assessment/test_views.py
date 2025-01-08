from urllib.parse import urlparse

import pytest
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from hawc.apps.assessment.forms import ContactForm
from hawc.apps.assessment.models import Assessment, Label
from hawc.apps.myuser.models import HAWCUser
from hawc.apps.study.models import Study

from ..test_utils import check_200, check_302, get_client


def has_redis():
    return "RedisCache" in settings.CACHES["default"]["BACKEND"]


class TestAssessmentClearCache:
    @pytest.mark.django_db
    def test_permissions(self, db_keys):
        url = Assessment.objects.get(id=db_keys.assessment_working).get_clear_cache_url()

        # test failures
        for client in ["reviewer@hawcproject.org", None]:
            c = Client()
            if client:
                assert c.login(username=client, password="pw") is True
            response = c.get(url)
            assert response.status_code == 403

        # test successes
        for client in ["pm@hawcproject.org", "team@hawcproject.org"]:
            c = Client()
            assert c.login(username=client, password="pw") is True
            response = c.get(url)
            assert response.status_code == 302

    @pytest.mark.django_db
    def test_functionality(self, db_keys):
        key1 = f"assessment-{db_keys.assessment_working}-test"
        key2 = f"assessment-{db_keys.assessment_working+1}-test"
        cache.set(key1, "exists")
        cache.set(key2, "exists")
        assert cache.get(key1) == "exists"
        assert cache.get(key2) == "exists"
        url = Assessment.objects.get(id=db_keys.assessment_working).get_clear_cache_url()
        c = Client()
        assert c.login(username="pm@hawcproject.org", password="pw") is True
        response = c.get(url)
        assert response.status_code == 302
        assert cache.get(key1) is None
        # special case; if using a redis cache we can keep other assessments
        if has_redis():
            assert cache.get(key2) == "exists"
        else:
            assert cache.get(key2) is None


@pytest.mark.django_db
class TestHomePage:
    def test_functionality(self):
        # anon
        anon_client = Client()
        url = reverse("home")
        response = anon_client.get(url)
        assert response.status_code == 200

        # auth
        rev_client = Client()
        assert rev_client.login(username="reviewer@hawcproject.org", password="pw") is True
        response = rev_client.get(url)
        assert response.status_code == 302

        # external
        settings.EXTERNAL_HOME = "."
        response = anon_client.get(url)
        assert urlparse(response.url).path == "."
        assert response.status_code == 302
        settings.EXTERNAL_HOME = ""


@pytest.mark.django_db
class TestAboutPage:
    def test_counts(self):
        client = Client()
        url = reverse("about")
        response = client.get(url)
        assert "counts" in response.context
        assert response.context["counts"]["assessments"] == 4
        assert response.context["counts"]["users"] == 5

    def test_settings_external(self):
        client = Client()
        url = reverse("about")
        settings.EXTERNAL_ABOUT = "."
        resp = client.get(url)
        assert resp.status_code == 302
        assert urlparse(resp.url).path == "."
        settings.EXTERNAL_ABOUT = ""

    def test_settings_hawc_flavor(self):
        client = Client()
        url = reverse("about")
        settings.HAWC_FLAVOR = "EPA"
        assert client.get(url).status_code == 200

        settings.HAWC_FLAVOR = "INVALID"
        with pytest.raises(ValueError):
            client.get(url)
        settings.HAWC_FLAVOR = "PRIME"


@pytest.mark.django_db
class TestAssessmentCreate:
    def test_permissions(self, settings):
        url = reverse("assessment:new")

        anon = Client()
        team = Client()
        admin = Client()
        assert team.login(username="team@hawcproject.org", password="pw") is True
        assert admin.login(username="admin@hawcproject.org", password="pw") is True

        settings.ANYONE_CAN_CREATE_ASSESSMENTS = True
        # login required
        resp = anon.get(url)
        assert resp.status_code == 302
        assert reverse("user:login") in resp.url

        # admin can create
        assert admin.get(url).status_code == 200

        # team can create
        assert team.get(url).status_code == 200

        settings.ANYONE_CAN_CREATE_ASSESSMENTS = False
        # login required
        resp = anon.get(url)
        assert resp.status_code == 302
        assert reverse("user:login") in resp.url

        # admin can create
        assert admin.get(url).status_code == 200

        # user can create with group
        resp = team.get(url)
        user = resp.wsgi_request.user
        assert resp.status_code == 403

        group = resp.wsgi_request.user.groups.get_or_create(name=HAWCUser.CAN_CREATE_ASSESSMENTS)[1]
        user.groups.add(group)
        user.refresh_from_db()
        assert team.get(url).status_code == 200


@pytest.mark.django_db
class TestResourcesPage:
    def test_functionality(self):
        client = Client()
        url = reverse("resources")
        assert client.get(url).status_code == 200

        # external
        settings.EXTERNAL_RESOURCES = "."
        resp = client.get(url)
        assert resp.status_code == 302
        assert urlparse(resp.url).path == "."
        settings.EXTERNAL_RESOURCES = ""


@pytest.mark.django_db
class TestAttachmentViewSet:
    def test_crud(self):
        client = get_client("pm", htmx=True)

        # create
        url = reverse("assessment:attachment-htmx", args=[1, "create"])
        resp = client.get(url)
        assert resp.status_code == 200
        assertTemplateUsed(resp, "assessment/fragments/attachment_edit_row.html")

        resp = client.post(
            url,
            {
                "attachment-new-title": "test",
                "attachment-new-description": "test",
                "attachment-new-attachment": SimpleUploadedFile("zzzz.txt", b"test"),
            },
            follow=True,
        )
        assert resp.status_code == 200
        assertTemplateUsed(resp, "assessment/fragments/attachment_row.html")

        instance_id = resp.context["object"].id

        # get (htmx)
        url = reverse("assessment:attachment-htmx", args=[instance_id, "read"])
        resp = client.get(url)
        assert resp.status_code == 200
        assertTemplateUsed(resp, "assessment/fragments/attachment_row.html")

        # get (download)
        client_no_htmx = get_client("admin")
        resp = client_no_htmx.get(url)
        assert resp.status_code == 302
        assert resp.url.startswith(settings.MEDIA_URL) and "zzzz" in resp.url and ".txt" in resp.url

        # update
        url = reverse("assessment:attachment-htmx", args=[instance_id, "update"])
        resp = client.get(url)
        assert resp.status_code == 200
        assertTemplateUsed(resp, "assessment/fragments/attachment_edit_row.html")

        resp = client.post(
            url,
            {
                f"attachment-{instance_id}-title": "test2",
                f"attachment-{instance_id}-description": "test2",
                f"attachment-{instance_id}-attachment": SimpleUploadedFile("test2.txt", b"test2"),
            },
            follow=True,
        )
        assert resp.status_code == 200
        assertTemplateUsed(resp, "assessment/fragments/attachment_row.html")

        # delete
        url = reverse("assessment:attachment-htmx", args=[instance_id, "delete"])
        resp = client.get(url)
        assert resp.status_code == 200
        assertTemplateUsed(resp, "assessment/fragments/attachment_row.html")
        assert resp.context["action"] == "delete"

        resp = client.post(url)
        assert resp.status_code == 200
        assert resp.content == b""


@pytest.mark.django_db
class TestContactUsPage:
    def test_login_required(self):
        contact_url = reverse("contact")

        client = Client()

        # login required
        resp = client.get(contact_url)
        assert resp.status_code == 302
        assert urlparse(resp.url).path == settings.LOGIN_URL

        # valid
        client.login(username="pm@hawcproject.org", password="pw")
        resp = client.get(contact_url)
        assert resp.status_code == 200

    def test_external(self):
        settings.EXTERNAL_CONTACT_US = "."
        contact_url = reverse("contact")
        client = Client()

        resp = client.get(contact_url)
        assert resp.status_code == 302
        assert urlparse(resp.url).path == "."
        settings.EXTERNAL_CONTACT_US = ""

    def test_referrer(self):
        contact_url = reverse("contact")
        client = Client(SERVER_NAME="testserver")
        domain = client._base_environ()["SERVER_NAME"]
        about_url = f"https://{domain}{reverse('about')}"
        portal_url = f"https://{domain}{reverse('portal')}"

        client.login(username="pm@hawcproject.org", password="pw")

        # no referrer; use default
        resp = client.get(contact_url)
        assert resp.context["form"].fields["previous_page"].initial == portal_url

        # valid referrer; use valid
        resp = client.get(contact_url, HTTP_REFERER=about_url)
        assert resp.context["form"].fields["previous_page"].initial == about_url

        # valid referer; remove arguments
        resp = client.get(contact_url, HTTP_REFERER=about_url + '?"onmouseover="alert(26)"')
        assert resp.context["form"].fields["previous_page"].initial == about_url

        # invalid referrer; use default
        resp = client.get(contact_url, HTTP_REFERER=about_url + '"onmouseover="alert(26)"')
        assert resp.context["form"].fields["previous_page"].initial == portal_url

    def test_turnstile(self, settings):
        anon = get_client()
        team = get_client("team")
        url = reverse("contact")

        # turnstile disabled
        settings.TURNSTILE_SITE = ""
        settings.TURNSTILE_KEY = ""

        # anon - redirect to login
        resp = anon.get(url, follow=True)
        check_302(anon, url, str(settings.LOGIN_URL))

        # auth - form displayed; no challenge
        resp = team.get(url, follow=True)
        form = resp.context["form"]
        assert isinstance(form, ContactForm)
        assert form.enable_turnstile is False

        # turnstile enabled
        settings.TURNSTILE_SITE = "https://test-me.org"
        settings.TURNSTILE_KEY = "secret"

        # anon - form displayed; has challenge
        resp = anon.get(url)
        form = resp.context["form"]
        assert isinstance(form, ContactForm)
        assert form.enable_turnstile is True

        # auth - form displayed; no challenge
        resp = team.get(url, follow=True)
        form = resp.context["form"]
        assert isinstance(form, ContactForm)
        assert form.enable_turnstile is False

        # turnstile disabled
        settings.TURNSTILE_SITE = ""
        settings.TURNSTILE_KEY = ""


@pytest.mark.django_db
class TestBulkPublishItems:
    def test_list(self):
        url = reverse("assessment:bulk-publish", args=(1,))

        anon = Client()
        pm = Client()
        assert pm.login(username="pm@hawcproject.org", password="pw") is True

        resp = anon.get(url)
        assert resp.status_code == 403

        resp = pm.get(url)
        assert resp.status_code == 200
        assertTemplateUsed(resp, "assessment/published_items.html")

    def test_updates_item(self):
        anon = Client(HTTP_HX_REQUEST="true")
        pm = Client(HTTP_HX_REQUEST="true")
        assert pm.login(username="pm@hawcproject.org", password="pw") is True

        # valid case
        assessment_id = 1
        study = Study.objects.filter(assessment=assessment_id).first()
        bad_study = Study.objects.filter(assessment=2).first()
        valid_url = reverse("assessment:publish-update", args=(assessment_id, "study", study.id))

        # permissions check
        resp = anon.post(valid_url)
        assert resp.status_code == 403

        # invalid url; study doesn't belong to assessment
        for bad_url in [
            reverse("assessment:publish-update", args=(assessment_id, "--invalid--", study.id)),
            reverse("assessment:publish-update", args=(assessment_id, "study", bad_study.id)),
        ]:
            resp = pm.post(bad_url)
            assert resp.status_code == 404

        # check initial state
        assert study.published is False

        # valid url
        resp = pm.post(valid_url)
        assert resp.status_code == 200
        assertTemplateUsed(resp, "assessment/fragments/publish_item_td.html")
        study.refresh_from_db()
        assert study.published is True

        # check opposite case (and revert state)
        resp = pm.post(valid_url)
        assert resp.status_code == 200
        assertTemplateUsed(resp, "assessment/fragments/publish_item_td.html")
        study.refresh_from_db()
        assert study.published is False

    def test_publish_label(self):
        label = Label.objects.get(id=2)
        assert label.published is True
        url = reverse("assessment:publish-update", args=(1, "label", label.id))
        pm = get_client("pm", api=False, htmx=True)
        pm.post(url)
        label.refresh_from_db()
        assert label.published is False
        label.published = True
        label.save()


@pytest.mark.django_db
class TestUpdateSession:
    def test_refresh(self):
        anon = get_client()
        pm = get_client("reviewer")

        url = reverse("update_session")

        resp = anon.post(url, data={})
        assert resp.status_code == 200
        assert resp.json() == {}

        resp = anon.post(url, data={"refresh": 1})
        assert resp.status_code == 404

        resp = pm.post(url, data={"refresh": 1})
        assert resp.status_code == 200
        assert "new_expiry_time" in resp.json()


class TestRasterizeCss:
    def test_check_success(self):
        url = reverse("css-rasterize")
        client = Client()
        resp = client.get(url)
        assert resp.status_code == 200
        assert resp.json()["template"].startswith('<defs><style type="text/css">')


@pytest.mark.django_db
class TestSearch:
    def test_success(self):
        anon = get_client()
        url = reverse("search")
        resp = anon.get(url, data={"all_public": "on", "query": "plotly", "type": "visual"})
        assert resp.status_code == 200
        assert resp.context["object_list"].count() == 1


@pytest.mark.django_db
def test_get_200():
    client = get_client("admin")
    main = 1
    log_content_type = 16
    log_obj_id = 1
    urls = [
        reverse("search"),
        reverse("assessment:full_list"),
        reverse("assessment:public_list"),
        reverse("assessment:detail", args=(main,)),
        reverse("assessment:update", args=(main,)),
        reverse("assessment:modules_update", args=(main,)),
        reverse("assessment:delete", args=(main,)),
        reverse("assessment:downloads", args=(main,)),
        reverse("assessment:assessment_logs", args=(main,)),
        reverse("assessment:details-create", args=(main,)),
        reverse("assessment:details-update", args=(main,)),
        reverse("assessment:values-create", args=(main,)),
        reverse("assessment:values-detail", args=(main,)),
        reverse("assessment:values-update", args=(main,)),
        reverse("assessment:values-delete", args=(main,)),
        reverse("assessment:log_object_list", args=(log_content_type, log_obj_id)),
        reverse("assessment:log_detail", args=(main,)),
        reverse("assessment:dataset_create", args=(main,)),
        reverse("assessment:dataset_detail", args=(main,)),
        reverse("assessment:dataset_update", args=(main,)),
        reverse("assessment:dataset_delete", args=(main,)),
        reverse("assessment:species_create", args=(main,)),
        reverse("assessment:strain_create", args=(main,)),
        reverse("assessment:dose_units_create", args=(main,)),
        reverse("assessment:dtxsid_create"),
        reverse("assessment:endpoint_list", args=(main,)),
        reverse("assessment:clean_extracted_data", args=(main,)),
        reverse("assessment:effect_tag_create", args=(main,)),
        reverse("assessment:content_types"),
        reverse("assessment:close_window"),
        reverse("assessment:clean_study_metrics", args=(main,)),
        reverse("assessment:bulk-publish", args=(main,)),
        reverse("assessment:labeled-items", args=(main,)),
        reverse("assessment:manage-labels", args=(main,)),
        reverse("assessment:bulk-publish", args=(main,)),
    ]
    for url in urls:
        check_200(client, url)
