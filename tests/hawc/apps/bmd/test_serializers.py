import pytest

from hawc.apps.bmd.constants import BmdInputSettings, SelectedModel
from hawc.apps.bmd.models import Session
from hawc.apps.bmd.serializers import SessionBmd3UpdateSerializer


@pytest.mark.django_db
class TestSessionBmd3UpdateSerializer:
    def test_validate_inputs(self):
        session = Session.objects.filter(version="BMDS330", active=True).first()
        schema = BmdInputSettings.create_default(endpoint=session.endpoint)

        # valid
        data = {"inputs": schema.dict()}
        serializer = SessionBmd3UpdateSerializer(data=data)
        assert serializer.is_valid() is True

        # invalid
        data = {"inputs": {**schema.dict(), **{"dtype": "Z"}}}
        serializer = SessionBmd3UpdateSerializer(data=data)
        assert serializer.is_valid() is False

    def test_validate_selected(self):
        schema = SelectedModel()

        # valid
        data = {"selected": schema.dict()}
        serializer = SessionBmd3UpdateSerializer(data=data)
        assert serializer.is_valid() is True

        # invalid
        data = {"selected": {**schema.dict(), **{"model_index": "A"}}}
        serializer = SessionBmd3UpdateSerializer(data=data)
        assert serializer.is_valid() is False
