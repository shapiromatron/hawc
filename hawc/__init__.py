"""A content management system for human health assessments."""

import os
import sys
from importlib.metadata import version

__version__ = version("hawc")


def manage():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hawc.main.settings.dev")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
