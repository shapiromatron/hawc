import pytest

from hawc.apps.assessment.models import Assessment
from hawc.apps.summary.constants import VisualType
from hawc.apps.summary.forms import ExternalSiteForm


@pytest.mark.django_db
class TestExternalSiteForm:
    def valid_data(self):
        return dict(
            title="title",
            slug="slug",
            description="hi",
            external_url="https://public.tableau.com/views/foo1/foo2?:display_count=y&:origin=viz_share_link",
            filters="[]",
        )

    def test_success(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        visual_type = VisualType.EXTERNAL_SITE

        data = self.valid_data()
        form = ExternalSiteForm(
            data=data,
            parent=assessment,
            visual_type=visual_type,
        )
        assert form.is_valid()
        assert form.cleaned_data == {
            "title": "title",
            "slug": "slug",
            "caption": "",
            "published": False,
            "external_url": "https://public.tableau.com/views/foo1/foo2",
            "external_url_hostname": "https://public.tableau.com",
            "external_url_path": "/views/foo1/foo2",
            "external_url_query_args": [":showVizHome=no", ":embed=y"],
            "filters": "[]",
        }

    def test_urls(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        visual_type = VisualType.EXTERNAL_SITE
        data = self.valid_data()
        # make sure our site allowlist works
        for url in [
            "google.com",
            "http://google.com",
            "https://google.com",
        ]:
            data["external_url"] = url
            form = ExternalSiteForm(data=data, parent=assessment, visual_type=visual_type)
            assert form.is_valid() is False
            assert "not on the list of accepted domains" in form.errors["external_url"][0]

        # make sure our path check works
        for url in [
            "public.tableau.com",
            "public.tableau.com/",
        ]:
            data["external_url"] = url
            form = ExternalSiteForm(data=data, parent=assessment, visual_type=visual_type)
            assert form.is_valid() is False
            assert "A URL path must be specified." == form.errors["external_url"][0]

    def test_filters(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        visual_type = VisualType.EXTERNAL_SITE
        data = self.valid_data()

        # test valid filters
        for filters in ["[]", '[{"field":"hi", "value":"ho"}]']:
            data["filters"] = filters
            form = ExternalSiteForm(data=data, parent=assessment, visual_type=visual_type)
            assert form.is_valid() is True

        # test invalid filters
        for filters in ["[123]", '[{"field":"hi"}]']:
            data["filters"] = filters
            form = ExternalSiteForm(data=data, parent=assessment, visual_type=visual_type)
            assert form.is_valid() is False
            assert "filters" in form.errors
