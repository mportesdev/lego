from django.db import models
from django.urls import reverse


class NumericPrefix(models.Func):
    function = "substring"
    template = "%(function)s(%(expressions)s from '^\\d+')"


class Shape(models.Model):
    lego_id = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    num_code = models.GeneratedField(
        expression=NumericPrefix("lego_id"),
        output_field=models.CharField(max_length=30),
        db_persist=True,
        null=True,
    )

    def __str__(self):
        return f"{self.lego_id} {self.name}"

    def __repr__(self):
        fields_repr = ", ".join(
            f"{field_name}={getattr(self, field_name)!r}"
            for field_name in ("id", "lego_id", "name", "num_code")
        )
        return f"{type(self).__name__}({fields_repr})"


class Color(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    def __repr__(self):
        fields_repr = ", ".join(
            f"{field_name}={getattr(self, field_name)!r}"
            for field_name in ("id", "name")
        )
        return f"{type(self).__name__}({fields_repr})"


class LegoPart(models.Model):
    shape = models.ForeignKey(Shape, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)
    image_url = models.URLField(null=True)
    image = models.CharField(max_length=100, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["shape", "color"], name="unique_shape_color"
            ),
        ]

    def get_absolute_url(self):
        kwargs = {"lego_id": self.shape.lego_id}
        if self.color:
            kwargs["color_id"] = self.color.id
        return reverse("part_detail", kwargs=kwargs)

    def __str__(self):
        return f"{self.shape}, {self.color}" if self.color else f"{self.shape}"

    def __repr__(self):
        fields_repr = ", ".join(
            f"{field_name}={getattr(self, field_name)!r}"
            for field_name in ("id", "shape", "color", "image_url", "image")
        )
        return f"{type(self).__name__}({fields_repr})"


class LegoSet(models.Model):
    lego_id = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    image_url = models.URLField(null=True)
    image = models.CharField(max_length=100, null=True)

    parts = models.ManyToManyField(LegoPart, through="SetItem", related_name="sets")

    def get_absolute_url(self):
        return reverse("set_detail", kwargs={"lego_id": self.lego_id})

    def __str__(self):
        return f"{self.lego_id} {self.name}"

    def __repr__(self):
        fields_repr = ", ".join(
            f"{field_name}={getattr(self, field_name)!r}"
            for field_name in ("id", "lego_id", "name", "image_url", "image")
        )
        return f"{type(self).__name__}({fields_repr})"


class SetItem(models.Model):
    set = models.ForeignKey(LegoSet, on_delete=models.CASCADE)
    part = models.ForeignKey(LegoPart, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["part__shape__name"]
