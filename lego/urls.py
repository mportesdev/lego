from django.urls import path

from .views import IndexView, SetDetail, PartDetail, search, add_set, login, logout

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("set/add/", add_set, name="add_set"),
    path("set/<lego_id>/", SetDetail.as_view(), name="set_detail"),
    path("part/<lego_id>/", PartDetail.as_view(), name="part_detail"),
    path("part/<lego_id>/<int:color_id>/", PartDetail.as_view(), name="part_detail"),
    path("search/", search, name="search"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
]
