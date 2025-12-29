"""
TODO - remove this file

This file should be removed when we can. Using a console_script named `manage` worked fine with
Django 3.2 However, when upgrading to Django 4.2, we now get an error:

$ manage runserver
> Error while finding module specification for '__main__' (ValueError: __main__.__spec__ is None)

Running `manage runserver --noreload` works fine.

This may be related to how console_scripts are configured in pyproject.toml.
"""

from hawc import manage

if __name__ == "__main__":
    manage()
