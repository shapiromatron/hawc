from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(Reference)
admin.site.register(Metadata)
admin.site.register(Cause)
admin.site.register(Effect)
admin.site.register(Quantitative)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(Ecoregion)
admin.site.register(Climate)
