from django.apps import AppConfig
from django.contrib.admin.apps import SimpleAdminConfig


class LegoAdminConfig(SimpleAdminConfig):
    default_site = "lego.admin.LegoAdminSite"


class LegoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "lego"
