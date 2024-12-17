import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView

from .external_api import get_set_info, get_set_parts
from .forms import SearchForm, AddSetForm
from .models import Shape, Color, LegoPart, LegoSet

COMMON_CONTEXT = {"site_name": "O&F Lego", "search_form": SearchForm}

logger = logging.getLogger(__name__)


class IndexView(ListView):
    model = LegoSet
    template_name = "lego/index.html"
    paginate_by = 24
    extra_context = COMMON_CONTEXT | {"title": "Home"}


def set_detail(request, lego_id):
    set_ = get_object_or_404(LegoSet, lego_id=lego_id)
    set_items = set_.setitem_set.all()
    return render(
        request,
        "lego/set_detail.html",
        context=COMMON_CONTEXT | {
            "image_url": set_.image_url,
            "set_items": set_items,
            "title": f"Lego Set {set_}",
        },
    )


def part_detail(request, lego_id, color_id=None):
    part = get_object_or_404(LegoPart, shape__lego_id=lego_id, color=color_id)
    set_items = part.setitem_set.all()
    return render(
        request,
        "lego/part_detail.html",
        context=COMMON_CONTEXT | {
            "image_url": part.image_url,
            "set_items": set_items,
            "title": f"Lego Part {part}",
        },
    )


def search(request):
    form = SearchForm(request.GET)
    if not form.is_valid():
        return render(
            request,
            "lego/search.html",
            context=COMMON_CONTEXT | {"title": "Search", "search_form": form},
        )

    search_string = form.cleaned_data["q"]
    search_mode = form.cleaned_data["mode"]

    name_q = Q(name__icontains=search_string)
    lego_id_q = Q(lego_id__startswith=search_string)
    shape_name_q = Q(shape__name__icontains=search_string)
    shape_lego_id_q = Q(shape__lego_id__startswith=search_string)
    color_name_q = Q(color__name__icontains=search_string)

    if search_mode == "name":
        sets = LegoSet.objects.filter(name_q)
        parts = LegoPart.objects.filter(shape_name_q)
    elif search_mode == "id":
        sets = LegoSet.objects.filter(lego_id_q)
        parts = LegoPart.objects.filter(shape_lego_id_q)
    elif search_mode == "color":
        sets = LegoSet.objects.none()  # sets don't have colors
        parts = LegoPart.objects.filter(color_name_q)
    else:
        sets = LegoSet.objects.filter(name_q | lego_id_q)
        parts = LegoPart.objects.filter(shape_name_q | shape_lego_id_q | color_name_q)

    return render(
        request,
        "lego/search.html",
        context=COMMON_CONTEXT | {
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
            context=COMMON_CONTEXT | {
                "add_set_form": AddSetForm,
                "title": "Add a New Lego Set",
            },
        )

    form = AddSetForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            "lego/add_set.html",
            context=COMMON_CONTEXT | {
                "add_set_form": form,
                "title": "Add a New Lego Set",
            },
        )

    set_lego_id = form.cleaned_data["set_lego_id"]
    if "-" not in set_lego_id:
        set_lego_id += "-1"

    set_, created = LegoSet.objects.get_or_create(lego_id=set_lego_id)
    if not created:
        logger.warning(f"Already exists: {set_!r}")
        return redirect("add_set")

    try:
        set_info = get_set_info(set_lego_id)
    except OSError as err:
        logger.error(f"Error calling external API: {err}")
        return redirect("add_set")

    set_.name = set_info["name"]
    set_.image_url = set_info["image_url"]
    set_.save()
    logger.info(f"Created: {set_!r}")

    for item in get_set_parts(set_lego_id):
        if item.get("is_spare"):
            logger.info(f"Skipping spare part: {item["name"]}, {item.get("color_name")}")
            continue
        shape = _get_shape(lego_id=item["lego_id"], name=item["name"])
        color_name = item.get("color_name")
        if color_name:
            color, created = Color.objects.get_or_create(name=color_name)
            if created:
                logger.info(f"Created: {color!r}")
        else:
            color = None
        part = _get_part(shape=shape, color=color, image_url=item["image_url"])
        set_.parts.add(part, through_defaults={"quantity": item["quantity"]})

    return redirect("set_detail", set_lego_id)


def _get_shape(lego_id, name):
    try:
        shape = Shape.objects.get(lego_id=lego_id)
        if shape.name != name:
            logger.warning(f"Outdated: {shape!r}")
            shape.name = name
            shape.save()
            logger.warning(f"Updated: {shape!r}")
    except Shape.DoesNotExist:
        shape = Shape.objects.create(lego_id=lego_id, name=name)
        logger.info(f"Created: {shape!r}")
    return shape


def _get_part(shape, color, image_url):
    try:
        part = LegoPart.objects.get(shape=shape, color=color)
        if part.image_url != image_url:
            logger.warning(f"Outdated: {part!r}")
            part.image_url = image_url
            part.save()
            logger.warning(f"Updated: {part!r}")
    except LegoPart.DoesNotExist:
        part = LegoPart.objects.create(shape=shape, color=color, image_url=image_url)
        logger.info(f"Created: {part!r}")
    return part


login = LoginView.as_view(
    template_name="lego/login.html",
    next_page="/lego/",
    extra_context=COMMON_CONTEXT,
)

logout = LogoutView.as_view(next_page="/lego/")
