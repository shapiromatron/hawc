import logging
import os
import sys
from pathlib import Path

import django

paths = [
    str(Path("..").resolve()),
    str(Path("../../hawc/project").resolve()),
]
sys.path.extend(paths)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hawc.settings.local")
django.setup()
logging.disable(logging.WARNING)

print("HAWC notebook environment loaded - ready to begin.")
