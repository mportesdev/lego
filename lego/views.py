from django.shortcuts import get_object_or_404, render

from .models import LegoPart, LegoSet


def index(request):
    sets = LegoSet.objects.all()
    return render(
        request,
        "lego/index.html",
        context={"sets": sets, "title": "Our Lego"},
    )


def set_detail(request, lego_id):
    set_ = get_object_or_404(LegoSet, lego_id=lego_id)
    set_items = set_.setitem_set.all()
    return render(
        request,
        "lego/set_detail.html",
        context={"set_items": set_items, "title": f"Lego Set {set_}"},
    )


def part_detail(request, lego_id):
    part = get_object_or_404(LegoPart, lego_id=lego_id)
    set_items = part.setitem_set.all()
    return render(
        request,
        "lego/part_detail.html",
        context={"set_items": set_items, "title": f"Lego Part {part}"},
    )
