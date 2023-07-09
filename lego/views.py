from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .forms import SearchForm
from .models import LegoPart, LegoSet


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


def part_detail(request, lego_id):
    part = get_object_or_404(LegoPart, lego_id=lego_id)
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

    name_q = Q(name__icontains=search_string)
    lego_id_q = Q(lego_id__startswith=search_string)

    sets = LegoSet.objects.filter(name_q | lego_id_q)
    parts = LegoPart.objects.filter(name_q | lego_id_q)

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
