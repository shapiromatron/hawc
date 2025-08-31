import pytest
from pybmds import __version__ as pybmds_version

from hawc.apps.animal.models import Endpoint
from hawc.apps.bmd.constants import SelectedModel
from hawc.apps.bmd.models import Session


@pytest.mark.django_db
class TestBmdSession:
    def test_dichotomous(self):
        # create new session w/ inputs
        session = Session.create_new(Endpoint.objects.get(id=8))
        assert session.version == pybmds_version
        settings = session.get_settings()
        assert settings.version == 2
        assert settings.dtype == "D"

        # execute
        assert session.date_executed is None
        session.execute()
        assert session.date_executed is not None
        assert len(session.outputs["models"]) == 11

        # select model
        assert session.active is False
        selected = SelectedModel(model_index=1, notes="notes!")
        session.set_selected_model(selected)
        assert session.active is True
        assert session.selected["model_index"] == 1
        assert session.outputs["selected"] == {"model_index": 1, "notes": "notes!"}

    def test_continuous(self):
        # create new session w/ inputs
        session = Session.create_new(Endpoint.objects.get(id=3))
        assert session.version == pybmds_version
        settings = session.get_settings()
        assert settings.version == 2
        assert settings.dtype == "C"

        # execute
        assert session.date_executed is None
        session.execute()
        assert session.date_executed is not None
        assert len(session.outputs["models"]) == 7

        # select model
        assert session.active is False
        selected = SelectedModel(model_index=2, notes="notes!")
        session.set_selected_model(selected)
        assert session.active is True
        assert session.selected["model_index"] == 2
        assert session.outputs["selected"] == {"model_index": 2, "notes": "notes!"}
