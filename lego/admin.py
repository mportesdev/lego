from django.contrib import admin

from .models import LegoPart, LegoSet, PartInSet

admin.site.register(LegoPart)
admin.site.register(LegoSet)
admin.site.register(PartInSet)
