from django.contrib import admin

from .models import Shape, Color, LegoPart, LegoSet, SetItem


class ShapeAdmin(admin.ModelAdmin):
    list_display = ["lego_id", "name"]


admin.site.register(Shape, ShapeAdmin)


class ColorAdmin(admin.ModelAdmin):
    list_display = ["name"]


admin.site.register(Color, ColorAdmin)


class LegoPartAdmin(admin.ModelAdmin):
    list_display = ["short_name", "shape", "color", "image_url"]
    list_filter = ["color"]
    search_fields = ["shape__lego_id", "shape__name", "color__name"]

    def short_name(self, obj):
        return (
            f"{obj.shape.lego_id} {obj.color}"
            if obj.color else f"{obj.shape.lego_id}"
        )


admin.site.register(LegoPart, LegoPartAdmin)


class LegoSetAdmin(admin.ModelAdmin):
    list_display = ["lego_id", "name", "image_url"]
    search_fields = ["lego_id", "name"]


admin.site.register(LegoSet, LegoSetAdmin)


class SetItemAdmin(admin.ModelAdmin):
    list_display = ["short_name", "set", "part", "quantity"]

    def short_name(self, obj):
        part_str = (
            f"{obj.part.shape.lego_id} {obj.part.color}"
            if obj.part.color else f"{obj.part.shape.lego_id}"
        )
        return f"{obj.quantity}x {part_str} in {obj.set.lego_id}"


admin.site.register(SetItem, SetItemAdmin)
