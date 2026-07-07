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

    class Meta:
        indexes = [
            models.Index(fields=["num_code"]),
        ]

    def __str__(self):
        return f"{self.lego_id} {self.name}"

    def __repr__(self):
        return _repr(self)


class Color(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    def __repr__(self):
        return _repr(self)


class Image(models.Model):
    path = models.CharField(max_length=150, null=True)
    origin_url = models.URLField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["path", "origin_url"], name="unique_path_and_origin"
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(path__isnull=False) | models.Q(origin_url__isnull=False)
                ),
                name="path_or_origin_not_null",
            ),
        ]

    def __str__(self):
        return self.path or self.origin_url

    def __repr__(self):
        return _repr(self)


class LegoPart(models.Model):
    shape = models.ForeignKey(Shape, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)
    image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True)

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
        return _repr(self)


class LegoSet(models.Model):
    lego_id = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True)

    parts = models.ManyToManyField(LegoPart, through="SetItem", related_name="sets")

    def get_absolute_url(self):
        return reverse("set_detail", kwargs={"lego_id": self.lego_id})

    def __str__(self):
        return f"{self.lego_id} {self.name}"

    def __repr__(self):
        return _repr(self)


class SetItem(models.Model):
    set = models.ForeignKey(LegoSet, on_delete=models.CASCADE)
    part = models.ForeignKey(LegoPart, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["part__shape__name"]

    def __repr__(self):
        return _repr(self)


def _repr(instance, field_names=None):
    if field_names is None:
        field_names = (field.attname for field in instance._meta.fields)

    fields_repr = ", ".join(
        f"{field_name}={getattr(instance, field_name)!r}"
        for field_name in field_names
    )
    return f"{instance._meta.object_name}({fields_repr})"
