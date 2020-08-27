def test(fail=False):
    if fail:
        raise Exception("FAILURE")
    return "SUCCESS"
