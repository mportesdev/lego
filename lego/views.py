import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import DetailView, ListView

from .api_calls import get_set_info
from .forms import SearchForm, AddSetForm
from .models import LegoPart, LegoSet
from .orm_utils import get_set, save_set_with_parts

logger = logging.getLogger(__name__)


class IndexView(ListView):
    template_name = "lego/index.html"
    paginate_by = 24
    extra_context = {"title": "Home"}

    def get_queryset(self):
        return LegoSet.objects.select_related("image").order_by("-pk")


class SetDetail(DetailView):
    template_name = "lego/set_detail.html"

    def get_queryset(self):
        return (
            LegoSet.objects
            .select_related("image")
            .prefetch_related(
                "setitem_set__part__shape",
                "setitem_set__part__color",
                "setitem_set__part__image",
            )
        )

    def get_object(self, **kwargs):
        return get_object_or_404(
            self.get_queryset(),
            lego_id=self.kwargs["lego_id"],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context | {"title": f"Lego Set {self.object}"}


class PartDetail(DetailView):
    template_name = "lego/part_detail.html"

    def get_queryset(self):
        return (
            LegoPart.objects
            .select_related("shape", "color", "image")
            .prefetch_related("setitem_set__set__image")
        )

    def get_object(self, **kwargs):
        return get_object_or_404(
            self.get_queryset(),
            shape__lego_id=self.kwargs["lego_id"],
            color=self.kwargs.get("color_id"),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context | {"title": f"Lego Part {self.object}"}


def search(request):
    form = SearchForm(request.GET)
    if not form.is_valid():
        return render(
            request,
            "lego/search.html",
            context={"title": "Search", "search_form": form},
        )

    search_string = form.cleaned_data["q"]
    search_mode = form.cleaned_data["mode"]

    name_q = Q(name__icontains=search_string)
    lego_id_q = Q(lego_id__startswith=search_string)
    shape_name_q = Q(shape__name__icontains=search_string)
    shape_num_code_q = Q(shape__num_code__exact=search_string)
    color_name_q = Q(color__name__icontains=search_string)

    if search_mode == "name":
        sets = LegoSet.objects.select_related("image").filter(name_q)
        parts = LegoPart.objects.select_related(
            "shape", "color", "image"
        ).filter(shape_name_q)
    elif search_mode == "id":
        sets = LegoSet.objects.select_related("image").filter(lego_id_q)
        parts = LegoPart.objects.select_related(
            "shape", "color", "image"
        ).filter(shape_num_code_q)
    elif search_mode == "color":
        sets = LegoSet.objects.none()  # sets don't have colors
        parts = LegoPart.objects.select_related(
            "shape", "color", "image"
        ).filter(color_name_q)
    else:
        sets = LegoSet.objects.select_related("image").filter(name_q | lego_id_q)
        parts = LegoPart.objects.select_related(
            "shape", "color", "image"
        ).filter(shape_name_q | shape_num_code_q | color_name_q)

    return render(
        request,
        "lego/search.html",
        context={
            "sets": sets,
            "parts": parts,
            "title": f"Search Results for {search_string!r}",
            "search_form": form,
        },
    )


@login_required(login_url="/lego/login")
def add_set(request):
    if request.method == "GET":
        return render(
            request,
            "lego/add_set.html",
            context={
                "add_set_form": AddSetForm,
                "title": "Add a New Lego Set",
            },
        )

    form = AddSetForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            "lego/add_set.html",
            context={
                "add_set_form": form,
                "title": "Add a New Lego Set",
            },
        )

    set_lego_id = form.cleaned_data["set_lego_id"]
    if "-" not in set_lego_id:
        set_lego_id += "-1"

    q = LegoSet.objects.filter(lego_id=set_lego_id)
    if q:
        set_ = q.get()
        logger.warning(f"Already exists: {set_!r}")
        messages.warning(
            request, f"Already exists: {set_}", extra_tags="is-warning"
        )
        return redirect("add_set")

    try:
        set_info = get_set_info(set_lego_id)
    except OSError as err:
        logger.error(f"Error calling external API: {err}")
        messages.error(
            request, f"Data not found: {set_lego_id}", extra_tags="is-danger"
        )
        return redirect("add_set")

    set_, _ = get_set(set_lego_id)
    save_set_with_parts(set_, set_info)
    messages.success(
        request, f"Added to queue: {set_}", extra_tags="is-success"
    )
    return redirect("add_set")


_login = LoginView.as_view(
    template_name="lego/login.html",
    next_page="/lego/",
    extra_context={"title": "Log in"},
)


def login(request, *args, **kwargs):
    response = _login(request, *args, **kwargs)
    if request.method == "POST":
        user = request.user
        if user.is_authenticated:
            logger.info(f"User logged in: {user.username}")
        else:
            username = request.POST["username"]
            logger.info(f"Failed user login: {username}")
    return response


_logout = LogoutView.as_view(next_page="/lego/")


def logout(request, *args, **kwargs):
    username = request.user.username
    response = _logout(request, *args, **kwargs)
    logger.info(f"User logged out: {username}")
    return response
