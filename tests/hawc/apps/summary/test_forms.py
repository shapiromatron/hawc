import json
from copy import deepcopy
from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from hawc.apps.assessment.models import Assessment
from hawc.apps.summary import forms
from hawc.apps.summary.constants import ExportStyle, StudyType, VisualType
from hawc.apps.summary.models import Visual


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
        form = forms.ExternalSiteForm(
            data=data,
            parent=assessment,
            visual_type=visual_type,
            evidence_type=StudyType.OTHER,
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
        instance = form.save()

        # check saved data loads on initial form
        form = forms.ExternalSiteForm(
            instance=instance,
            data=data,
        )
        assert form.fields["external_url"].initial == "https://public.tableau.com/views/foo1/foo2"

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
            form = forms.ExternalSiteForm(data=data, parent=assessment, visual_type=visual_type)
            assert form.is_valid() is False
            assert "not on the list of accepted domains" in form.errors["external_url"][0]

        # make sure our path check works
        for url in [
            "public.tableau.com",
            "public.tableau.com/",
        ]:
            data["external_url"] = url
            form = forms.ExternalSiteForm(data=data, parent=assessment, visual_type=visual_type)
            assert form.is_valid() is False
            assert "A URL path must be specified." == form.errors["external_url"][0]

    def test_filters(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        visual_type = VisualType.EXTERNAL_SITE
        data = self.valid_data()

        # test valid filters
        for filters in ["[]", '[{"field":"hi", "value":"ho"}]']:
            data["filters"] = filters
            form = forms.ExternalSiteForm(data=data, parent=assessment, visual_type=visual_type)
            assert form.is_valid() is True

        # test invalid filters
        for filters in ["[123]", '[{"field":"hi"}]']:
            data["filters"] = filters
            form = forms.ExternalSiteForm(data=data, parent=assessment, visual_type=visual_type)
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
class TestEndpointAggregationForm:
    def test_success(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        visual_type = VisualType.BIOASSAY_AGGREGATION
        # check save works and settings are saved correctly
        form = forms.EndpointAggregationForm(
            data={
                "title": "test",
                "slug": "test",
                "dose_units": 1,
                "endpoints": [1],
            },
            parent=assessment,
            visual_type=visual_type,
            evidence_type=StudyType.BIOASSAY,
        )
        assert form.is_valid()


@pytest.mark.django_db
class TestTagtreeForm:
    def valid_data(self):
        return dict(
            title="title",
            slug="slug",
            description="hi",
            root_node=1,
            required_tags=[],
            pruned_tags=[],
            hide_empty_tag_nodes=False,
            height=500,
            width=999,
            show_legend=True,
            show_counts=True,
        )

    def test_success(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        visual_type = VisualType.LITERATURE_TAGTREE

        # check save works and settings are saved correctly
        data = self.valid_data()
        form = forms.TagtreeForm(
            data=data,
            parent=assessment,
            visual_type=visual_type,
            evidence_type=StudyType.OTHER,
        )
        assert form.is_valid()
        instance = form.save()
        assert instance.settings == {
            "root_node": 1,
            "required_tags": [],
            "pruned_tags": [],
            "hide_empty_tag_nodes": False,
            "width": 999,
            "height": 500,
            "show_legend": True,
            "show_counts": True,
        }

        # check saved data loads on initial form
        form = forms.TagtreeForm(
            instance=instance,
            data=data,
        )
        assert form.fields["width"].initial == 999


@pytest.mark.django_db
class TestPlotlyVisualForm:
    def _build_form(self, data: dict) -> forms.PlotlyVisualForm:
        return forms.PlotlyVisualForm(
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


def create_image(
    size: tuple[int, int], image_mode: str = "RGB", image_format: str = "PNG"
) -> bytes:
    """
    Generate a test image, returning a BytesIO of the image data.

    from https://stackoverflow.com/questions/11170425/how-to-unit-test-file-upload-in-django
    """
    data = BytesIO()
    Image.new(image_mode, size).save(data, image_format)
    return data.getvalue()


@pytest.mark.django_db
class TestImageVisualForm:
    def test_valid(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        visual_type = VisualType.IMAGE
        file = SimpleUploadedFile("file.png", create_image((2000, 2000)), content_type="image/png")
        data = dict(title="title", slug="slug", caption="hi")
        data.update({"settings-alt_text": "hi"})
        form = forms.ImageVisualForm(
            data=data, files={"image": file}, parent=assessment, visual_type=visual_type
        )
        assert form.is_valid()

    def test_clean_image(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        visual_type = VisualType.IMAGE

        # wrong extension
        file = SimpleUploadedFile("file.txt", create_image((2000, 2000)), content_type="image/png")
        data = dict(title="title", slug="slug", caption="hi")
        form = forms.ImageVisualForm(
            data=data, files={"image": file}, parent=assessment, visual_type=visual_type
        )
        assert form.is_valid() is False
        assert "File extension “txt” is not allowed." in form.errors["image"][0]

        # wrong size
        file = SimpleUploadedFile("file.png", create_image((5, 5)), content_type="image/png")
        data = dict(title="title", slug="slug", caption="hi")
        form = forms.ImageVisualForm(
            data=data, files={"image": file}, parent=assessment, visual_type=visual_type
        )
        assert form.is_valid() is False
        assert "Image must be >10KB and <3 MB in size." in form.errors["image"][0]


@pytest.mark.django_db
class TestDataPivotDatasetForm:
    def test_success(self, db_keys):
        form = forms.DataPivotDatasetForm(
            parent=Assessment.objects.get(id=db_keys.assessment_final),
            visual_type=VisualType.DATA_PIVOT_FILE,
            data={
                "title": "title",
                "slug": "title",
                "dataset": 2,
            },
        )
        assert form.is_valid() is True
        assert len(form.render()) > 0


@pytest.mark.django_db
class TestDataPivotQueryForm:
    def test_empty(self, db_keys):
        form = forms.DataPivotQueryForm(
            parent=Assessment.objects.get(id=db_keys.assessment_working),
            visual_type=VisualType.DATA_PIVOT_QUERY,
            evidence_type=StudyType.BIOASSAY,
            data=None,
        )
        assert len(form.render()) > 0

    def test_create(self, db_keys):
        form = forms.DataPivotQueryForm(
            parent=Assessment.objects.get(id=db_keys.assessment_working),
            visual_type=VisualType.DATA_PIVOT_QUERY,
            evidence_type=StudyType.BIOASSAY,
            data={
                "title": "title",
                "slug": "slug",
                "export_style": ExportStyle.EXPORT_ENDPOINT.value,
            },
        )
        assert form.is_valid()

        # assert save successfully works
        assert form.instance.id is None
        form.save()
        assert form.instance.id is not None

    def test_update(self, db_keys):
        form = forms.DataPivotQueryForm(
            parent=Assessment.objects.get(id=db_keys.assessment_working),
            visual_type=VisualType.DATA_PIVOT_QUERY,
            evidence_type=StudyType.BIOASSAY,
            data={
                "title": "title",
                "slug": "slug",
                "export_style": ExportStyle.EXPORT_ENDPOINT.value,
            },
            instance=Visual.objects.get(id=17),
        )
        assert form.is_valid()


@pytest.mark.django_db
class TestVisualSelectorForm:
    def test_success(self, db_keys):
        form = forms.VisualSelectorForm(
            parent=Assessment.objects.get(id=db_keys.assessment_final),
            queryset=Visual.objects.filter(assessment=db_keys.assessment_final),
            visual_type=VisualType.DATA_PIVOT_QUERY,
            data={"selector": 17, "reset_row_overrides": True},
        )
        assert form.is_valid()
        assert (
            form.get_success_url()
            == "/summary/assessment/2/visuals/10/create/?initial=17&reset_row_overrides=1"
        )
