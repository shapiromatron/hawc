import time

from hawc.apps.common import helper


def test_create_uuid():
    # Make sure UUID creation is stable over time
    id_1 = 1234
    uuid_1 = helper.create_uuid(id_1)
    time.sleep(1)
    assert uuid_1 == helper.create_uuid(id_1)

    # Simple test to ensure our UUID creation is unique
    id_2 = 12345
    uuid_2 = helper.create_uuid(id_2)
    assert uuid_1 != uuid_2


class TestFlatFileExporter:
    def test_get_flattened_tags(self):
        # check if key doesn't exist
        assert helper.FlatFileExporter.get_flattened_tags({}, "nope") == "||"

        # check if key doesn't exist but no values
        assert helper.FlatFileExporter.get_flattened_tags({"hi": []}, "hi") == "||"

        # check if key exists and there are values
        assert (
            helper.FlatFileExporter.get_flattened_tags({"hi": [{"name": "a"}, {"name": "b"}]}, "hi")
            == "|a|b|"
        )
