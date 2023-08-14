from django.shortcuts import render

from .models import LegoPart, LegoSet


def index(request):
    sets = LegoSet.objects.all()
    return render(
        request,
        "lego/index.html",
        context={"sets": sets, "title": "Our Lego"},
    )


def set_detail(request, lego_id):
    set_ = LegoSet.objects.get(lego_id=lego_id)
    parts = set_.parts.all()
    return render(
        request,
        "lego/set_detail.html",
        context={"parts": parts, "title": f"Lego Set {set_}"},
    )


def part_detail(request, lego_id):
    part = LegoPart.objects.get(lego_id=lego_id)
    sets = part.sets.all()
    return render(
        request,
        "lego/part_detail.html",
        context={"sets": sets, "title": f"Lego Part {part}"},
    )
