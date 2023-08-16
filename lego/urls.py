from django.urls import path

from .views import index, set_detail, part_detail

urlpatterns = [
    path("", index, name="index"),
    path("set/<lego_id>/", set_detail, name="set_detail"),
    path("part/<lego_id>/", part_detail, name="part_detail"),
]
