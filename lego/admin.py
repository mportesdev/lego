from django.contrib import admin

from .models import Shape, Color, Image, LegoPart, LegoSet, SetItem


class LegoAdminSite(admin.AdminSite):
    site_url = "/lego/"
    site_header = "Lego Administration"
    site_title = "Lego Admin"


admin_site = LegoAdminSite(name="lego_admin")


class ShapeAdmin(admin.ModelAdmin):
    list_display = ["lego_id", "name", "num_code"]
    search_fields = ["lego_id", "name"]
    readonly_fields = ["num_code"]


admin_site.register(Shape, ShapeAdmin)


class ColorAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


admin_site.register(Color, ColorAdmin)


class ImageAdmin(admin.ModelAdmin):
    list_display = ["path", "origin_url"]


admin_site.register(Image, ImageAdmin)


class LegoPartAdmin(admin.ModelAdmin):
    list_display = ["shape", "color", "image"]
    list_filter = ["color"]
    search_fields = ["shape__lego_id", "shape__name", "color__name"]


admin_site.register(LegoPart, LegoPartAdmin)


class LegoSetAdmin(admin.ModelAdmin):
    list_display = ["lego_id", "name", "image"]
    search_fields = ["lego_id", "name"]


admin_site.register(LegoSet, LegoSetAdmin)


class SetItemAdmin(admin.ModelAdmin):
    list_display = ["set", "part", "quantity"]
    list_select_related = ["set", "part__shape", "part__color"]


admin_site.register(SetItem, SetItemAdmin)


# register admins from django
from django.contrib.auth.admin import Group, GroupAdmin, User, UserAdmin

admin_site.register(Group, GroupAdmin)
admin_site.register(User, UserAdmin)

# register admin from django-tasks
from django_tasks_db.admin import DBTaskResult, DBTaskResultAdmin

admin_site.register(DBTaskResult, DBTaskResultAdmin)
