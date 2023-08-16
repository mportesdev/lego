from django.db import models


class LegoPart(models.Model):
    lego_id = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.lego_id} {self.name}"


class LegoSet(models.Model):
    lego_id = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)

    parts = models.ManyToManyField(LegoPart)

    def __str__(self):
        return f"{self.lego_id} {self.name}"
