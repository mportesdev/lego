from django.contrib import admin

from .models import Shape, Color, LegoPart, LegoSet, SetItem

admin.site.register(Shape)
admin.site.register(Color)
admin.site.register(LegoPart)
admin.site.register(LegoSet)
admin.site.register(SetItem)
