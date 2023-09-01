import logging

from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect

from .external_api import get_set_info, get_set_parts
from .forms import SearchForm, AddSetForm
from .models import Shape, Color, LegoPart, LegoSet

logger = logging.getLogger(__name__)


def index(request):
    sets = LegoSet.objects.all()
    return render(
        request,
        "lego/index.html",
        context={
            "sets": sets,
            "title": "Our Lego",
            "search_form": SearchForm(),
        },
    )


def set_detail(request, lego_id):
    set_ = get_object_or_404(LegoSet, lego_id=lego_id)
    relations = set_.partinset_set.all()
    return render(
        request,
        "lego/set_detail.html",
        context={
            "relations": relations,
            "title": f"Lego Set {set_}",
            "search_form": SearchForm(),
        },
    )


def part_detail(request, lego_id, color_id=None):
    part = get_object_or_404(LegoPart, shape__lego_id=lego_id, color=color_id)
    relations = part.partinset_set.all()
    return render(
        request,
        "lego/part_detail.html",
        context={
            "relations": relations,
            "title": f"Lego Part {part}",
            "search_form": SearchForm(),
        },
    )


def search(request):
    search_string = request.GET["q"]
    search_mode = request.GET["mode"]

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
        context={
            "sets": sets,
            "parts": parts,
            "title": f"Search Results for {search_string!r}",
            "search_form": SearchForm(request.GET),
        },
    )


def add_set(request):
    if request.method == "GET":
        return render(
            request,
            "lego/add_set.html",
            context={
                "add_set_form": AddSetForm(),
                "title": "Add a New Lego Set",
                "search_form": SearchForm(),
            },
        )

    set_lego_id = request.POST["set_lego_id"]
    if "-" not in set_lego_id:
        set_lego_id += "-1"

    set_, created = LegoSet.objects.get_or_create(lego_id=set_lego_id)
    if not created:
        logger.warning(f"{set_} already exists")
        return redirect("add_set")

    try:
        set_info = get_set_info(set_lego_id)
    except OSError as err:
        logger.error(f"Error calling external API: {err}")
        return redirect("add_set")

    set_.name = set_info["name"]
    set_.save()
    for item in get_set_parts(set_lego_id):
        shape = Shape.objects.get_or_create(
            lego_id=item["lego_id"], name=item["name"]
        )[0]
        color_name = item["color_name"]
        color = Color.objects.get_or_create(name=color_name)[0] if color_name else None
        part = LegoPart.objects.get_or_create(shape=shape, color=color)[0]
        set_.parts.add(part, through_defaults={"quantity": item["quantity"]})
    return redirect("set_detail", set_lego_id)
