from django.urls import path, include

from lego.admin import admin_site

urlpatterns = [
    path("admin/", admin_site.urls),
    path("lego/", include("lego.urls")),
]

from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns.extend(debug_toolbar_urls())
