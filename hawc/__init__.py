"""A content management system for human health assessments."""
__version__ = "0.1"

import os
import platform
import sys


def manage():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hawc.main.settings.dev")
    from django.core.management import execute_from_command_line

    # Setuptools generate entry point scripts with "-script.py" appended
    # to the end of them in Windows
    if platform.system() == "Windows":
        sys.argv[0] += "-script.py"

    execute_from_command_line(sys.argv)
