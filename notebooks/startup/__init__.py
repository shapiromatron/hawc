import os
import sys

sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('../../hawc/project'))

import logging
import django

django.setup()
logging.disable(logging.WARNING)

print('HAWC notebook environment loaded - ready to begin.')
