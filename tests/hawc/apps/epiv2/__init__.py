from django.apps import apps


# do not load tests if app is not installed
def load_tests(loader, tests, pattern):
    if apps.is_installed("hawc.apps.epiv2"):
        pass
