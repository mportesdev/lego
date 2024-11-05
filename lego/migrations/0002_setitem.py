# Generated by Django 5.1.3 on 2024-11-05 14:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lego", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="legoset",
            old_name="parts",
            new_name="parts_old",
        ),
        migrations.CreateModel(
            name="SetItem",
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
                ("quantity", models.PositiveSmallIntegerField(default=1)),
                (
                    "part",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="lego.legopart"
                    ),
                ),
                (
                    "set",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="lego.legoset"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="legoset",
            name="parts",
            field=models.ManyToManyField(
                related_name="sets", through="lego.SetItem", to="lego.legopart"
            ),
        ),
        migrations.RemoveField(
            model_name="legoset",
            name="parts_old",
        ),
    ]