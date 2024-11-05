from django.contrib import admin

from .models import LegoPart, LegoSet, SetItem

admin.site.register(LegoPart)
admin.site.register(LegoSet)
admin.site.register(SetItem)
