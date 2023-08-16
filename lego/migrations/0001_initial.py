# Generated by Django 4.2.4 on 2023-08-22 22:37

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="LegoPart",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("lego_id", models.CharField(max_length=30, unique=True)),
                ("name", models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name="LegoSet",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("lego_id", models.CharField(max_length=30, unique=True)),
                ("name", models.CharField(max_length=150)),
                ("parts", models.ManyToManyField(to="lego.legopart")),
            ],
        ),
    ]