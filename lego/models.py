from django.db import models


class Shape(models.Model):
    lego_id = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.lego_id} {self.name}"


class Color(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class LegoPart(models.Model):
    shape = models.ForeignKey(Shape, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.shape}, {self.color}" if self.color else f"{self.shape}"


class LegoSet(models.Model):
    lego_id = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)

    parts = models.ManyToManyField(LegoPart, through="PartInSet", related_name="sets")

    def __str__(self):
        return f"{self.lego_id} {self.name}"


class PartInSet(models.Model):
    set = models.ForeignKey(LegoSet, on_delete=models.CASCADE)
    part = models.ForeignKey(LegoPart, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)
