import os
import sys


def manage():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hawc.main.settings.local")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
