from django.contrib import admin

from .models import Shape, Color, LegoPart, LegoSet, SetItem


class LegoAdminSite(admin.AdminSite):
    site_url = "/lego/"
    site_header = "Lego Administration"
    site_title = "Lego Admin"


admin_site = LegoAdminSite(name="lego_admin")


class ShapeAdmin(admin.ModelAdmin):
    list_display = ["lego_id", "name"]


admin_site.register(Shape, ShapeAdmin)


class ColorAdmin(admin.ModelAdmin):
    list_display = ["name"]


admin_site.register(Color, ColorAdmin)


class LegoPartAdmin(admin.ModelAdmin):
    list_display = ["short_name", "shape", "color", "image_url", "image"]
    list_filter = ["color"]
    search_fields = ["shape__lego_id", "shape__name", "color__name"]

    def short_name(self, obj):
        return (
            f"{obj.shape.lego_id} {obj.color}"
            if obj.color else f"{obj.shape.lego_id}"
        )


admin_site.register(LegoPart, LegoPartAdmin)


class LegoSetAdmin(admin.ModelAdmin):
    list_display = ["lego_id", "name", "image_url", "image"]
    search_fields = ["lego_id", "name"]


admin_site.register(LegoSet, LegoSetAdmin)


class SetItemAdmin(admin.ModelAdmin):
    list_display = ["short_name", "set", "part", "quantity"]

    def short_name(self, obj):
        part_str = (
            f"{obj.part.shape.lego_id} {obj.part.color}"
            if obj.part.color else f"{obj.part.shape.lego_id}"
        )
        return f"{obj.quantity}x {part_str} in {obj.set.lego_id}"


admin_site.register(SetItem, SetItemAdmin)


# register admins from django
from django.contrib.auth.admin import Group, GroupAdmin, User, UserAdmin

admin_site.register(Group, GroupAdmin)
admin_site.register(User, UserAdmin)

# register admin from django-tasks
from django_tasks.backends.database.admin import DBTaskResult, DBTaskResultAdmin

admin_site.register(DBTaskResult, DBTaskResultAdmin)
