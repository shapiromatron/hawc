from datetime import datetime
import json

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.urlresolvers import reverse
from assessment import models
from assessment.models import Species, Strain

