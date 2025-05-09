import pytest

from hawc.apps.bmd.constants import BmdInputSettings, SelectedModel
from hawc.apps.bmd.models import Session
from hawc.apps.bmd.serializers import SessionBmdUpdateSerializer


@pytest.mark.django_db
class TestSessionBmdUpdateSerializer:
    def test_validate_inputs(self):
        session = Session.objects.filter(version="24.1", active=True).first()
        schema = BmdInputSettings.create_default(endpoint=session.endpoint)

        # valid
        data = {"inputs": schema.model_dump()}
        serializer = SessionBmdUpdateSerializer(data=data)
        assert serializer.is_valid() is True

        # invalid
        data = {"inputs": {**schema.model_dump(), **{"dtype": "Z"}}}
        serializer = SessionBmdUpdateSerializer(data=data)
        assert serializer.is_valid() is False

    def test_validate_selected(self):
        schema = SelectedModel()

        # valid
        data = {"selected": schema.model_dump()}
        serializer = SessionBmdUpdateSerializer(data=data)
        assert serializer.is_valid() is True

        # invalid
        data = {"selected": {**schema.model_dump(), **{"model_index": "A"}}}
        serializer = SessionBmdUpdateSerializer(data=data)
        assert serializer.is_valid() is False
