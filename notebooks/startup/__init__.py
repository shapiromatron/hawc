from pathlib import Path
import os
import sys

paths = [
    str(Path('..').resolve()),
    str(Path('../../hawc/project').resolve()),
]
sys.path.extend(paths)


import logging  # noqa: E402
import django  # noqa: E402


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hawc.settings.local")
django.setup()
logging.disable(logging.WARNING)

print('HAWC notebook environment loaded - ready to begin.')
