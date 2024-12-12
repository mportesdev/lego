from django.urls import path, include

from lego.admin import admin_site

urlpatterns = [
    path("admin/", admin_site.urls),
    path("lego/", include("lego.urls")),
]
