from django.contrib import admin

from .models import Shape, LegoPart, LegoSet, PartInSet

admin.site.register(Shape)
admin.site.register(LegoPart)
admin.site.register(LegoSet)
admin.site.register(PartInSet)
