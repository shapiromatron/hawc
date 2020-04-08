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
