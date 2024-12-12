from django.urls import path, include

from lego.admin import admin_site

urlpatterns = [
    path("admin/", admin_site.urls),
    path("lego/", include("lego.urls")),
]

from django.shortcuts import redirect

urlpatterns.append(path("", lambda r: redirect("/lego/")))
