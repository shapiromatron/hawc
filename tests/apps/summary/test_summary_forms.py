import pytest

from hawc.apps.assessment.models import Assessment
from hawc.apps.summary.forms import ExternalSiteForm
from hawc.apps.summary.models import Visual


@pytest.mark.django_db
def test_ExternalSiteForm(db_keys):
    assessment = Assessment.objects.get(id=db_keys.assessment_working)
    visual_type = Visual.EXTERNAL_SITE

    data = dict(
        title="title",
        slug="slug",
        description="hi",
        external_url="https://public.tableau.com/views/foo1/foo2?:display_count=y&:origin=viz_share_link",
    )

    # demo what success looks like
    form = ExternalSiteForm(data=data, parent=assessment, visual_type=visual_type,)
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
    }

    # make sure our site whitelist works
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
