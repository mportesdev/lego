from django.urls import path

from .views import index, set_detail, part_detail, search, add_set, login, logout

urlpatterns = [
    path("", index, name="index"),
    path("set/add/", add_set, name="add_set"),
    path("set/<lego_id>/", set_detail, name="set_detail"),
    path("part/<lego_id>/", part_detail, name="part_detail"),
    path("part/<lego_id>/<int:color_id>/", part_detail, name="part_detail"),
    path("search/", search, name="search"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
]
