"""
TODO - remove this file

This file should be removed when we can. Using a console_script named `manage` worked fine with
Django 3.2 However, when upgrading to Django 4.2, we now get an error:

$ manage runserver
> Error while finding module specification for '__main__' (ValueError: __main__.__spec__ is None)

Running `manage runserver --noreload` works fine.

To fix, update our build/packaging system to flit or poetry and call console_scripts as a module
instead of a file, which may fix this issue, based on work on other (private) projects?
"""

from hawc import manage

if __name__ == "__main__":
    manage()
