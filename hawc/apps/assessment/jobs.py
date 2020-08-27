def test(self, fail=False):
    if fail:
        raise Exception("FAILURE")
    return "SUCCESS"
