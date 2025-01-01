import pytest
from plotly.graph_objs import Figure
from rest_framework.exceptions import ValidationError

from hawc.apps.assessment.models import EffectTag
from hawc.apps.assessment.serializers import GrowthPlotSerializer, RelatedEffectTagSerializer


@pytest.mark.django_db
class TestRelatedEffectTagSerializer:
    def test_to_internal_value(self):
        tag = EffectTag.objects.first()
        ser = RelatedEffectTagSerializer()

        # given a proper tag name; return tag
        assert ser.to_internal_value(tag.name).id == tag.id

        # invalid type
        with pytest.raises(ValidationError):
            ser.to_internal_value(-1)

        # invalid name
        assert EffectTag.objects.filter(name="not a tag").exists() is False
        with pytest.raises(ValidationError):
            ser.to_internal_value("not a tag")


@pytest.mark.django_db
class TestGrowthPlotSerializer:
    def test_create_figure(self):
        for model, group in [["user", "YE"], ["assessment", "QE"], ["study", "ME"]]:
            serializer = GrowthPlotSerializer(data={"model": model, "grouper": group})
            assert serializer.is_valid()
            fig = serializer.create_figure()
            assert isinstance(fig, Figure)
