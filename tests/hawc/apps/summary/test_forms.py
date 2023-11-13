import json
from copy import deepcopy
from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from hawc.apps.assessment.models import Assessment
from hawc.apps.summary.constants import VisualType
from hawc.apps.summary.forms import ExternalSiteForm, ImageVisualForm, PlotlyVisualForm


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


@pytest.fixture
def valid_plotly_data() -> dict:
    return {
        "title": "title",
        "slug": "slug",
        "settings": '{"data": [{"orientation": "h", "x": [1, 2, 3], "xaxis": "x", "y": [0, 1, 2], "yaxis": "y", "type": "bar"}], "layout": {"title":{"text":"test"}}}',
    }


@pytest.mark.django_db
class TestPlotlyVisualForm:
    def _build_form(self, data: dict) -> PlotlyVisualForm:
        return PlotlyVisualForm(
            parent=Assessment.objects.first(), visual_type=VisualType.PLOTLY, data=data
        )

    def test_valid(self, valid_plotly_data: dict):
        form = self._build_form(valid_plotly_data)
        assert form.is_valid()

    def test_settings_validation(self, valid_plotly_data):
        # invalid settings or plotly configuration
        for bad_settings in ["", "not JSON", "{}", '{"plotly": false}']:
            data = deepcopy(valid_plotly_data)
            data["settings"] = bad_settings
            form = self._build_form(data)
            assert not form.is_valid()
            assert "settings" in form.errors

        # valid plotly configuration, but additional undesirable items
        for bad_title in [
            "<script>alert('hi')</script>",
            "<script>",
            "href='http://www.example.com'",
        ]:
            data = deepcopy(valid_plotly_data)
            settings = json.loads(valid_plotly_data["settings"])
            settings["layout"]["title"] = bad_title
            data["settings"] = json.dumps(settings)
            form = self._build_form(data)
            assert not form.is_valid()
            assert "settings" in form.errors


def create_image(size=(100, 100), image_mode="RGB", image_format="PNG"):
    """
    Generate a test image, returning a BytesIO of the image data.

    from https://stackoverflow.com/questions/11170425/how-to-unit-test-file-upload-in-django
    """
    data = BytesIO()
    Image.new(image_mode, size).save(data, image_format)
    data.seek(0)
    return data


@pytest.mark.django_db
class TestImageVisualForm:
    def test_valid(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        visual_type = VisualType.IMAGE
        image = create_image((10000, 10000))
        file = SimpleUploadedFile(
            "file.png",
            image.getvalue(),
            content_type="image/png",
        )

        data = dict(
            title="title",
            slug="slug",
            caption="hi",
        )
        form = ImageVisualForm(
            data=data, files={"image": file}, parent=assessment, visual_type=visual_type
        )
        assert form.is_valid()

    def test_filename(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        visual_type = VisualType.IMAGE

        file = SimpleUploadedFile(
            "file.txt",
            b"",
        )

        data = dict(
            title="title",
            slug="slug",
            caption="hi",
        )
        form = ImageVisualForm(
            data=data, files={"image": file}, parent=assessment, visual_type=visual_type
        )
        assert form.is_valid() is False

    def test_file_size(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        visual_type = VisualType.IMAGE

        # small image
        image = create_image((10, 10))
        file = SimpleUploadedFile(
            "file.png",
            image.getvalue(),
            content_type="image/png",
        )
        data = dict(
            title="title",
            slug="slug",
            caption="hi",
        )
        form = ImageVisualForm(
            data=data, files={"image": file}, parent=assessment, visual_type=visual_type
        )
        assert form.is_valid() is False

        # big image
        image = create_image((30000, 30000))
        file = SimpleUploadedFile(
            "file.png",
            image.getvalue(),
            content_type="image/png",
        )
        form = ImageVisualForm(
            data=data, files={"image": file}, parent=assessment, visual_type=visual_type
        )
        assert form.is_valid() is False
