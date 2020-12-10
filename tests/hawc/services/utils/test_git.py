from hawc.services.utils.git import Commit


class TestCommit:
    def test_current(self):
        # test that the current Commit method works; must be tested in a git repo w/ git installed
        Commit.current()
