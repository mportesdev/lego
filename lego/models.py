from django.db import models


class LegoPart(models.Model):
    lego_id = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.lego_id} {self.name}"


class LegoSet(models.Model):
    lego_id = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)

    parts = models.ManyToManyField(LegoPart, through="SetItem", related_name="sets")

    def __str__(self):
        return f"{self.lego_id} {self.name}"


class SetItem(models.Model):
    set = models.ForeignKey(LegoSet, on_delete=models.CASCADE)
    part = models.ForeignKey(LegoPart, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)
