# Generated by Django 4.2.5 on 2023-09-25 08:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("lego", "0002_rename_parts_legoset_parts_old_partinset_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Shape",
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
        migrations.RemoveField(
            model_name="legopart",
            name="lego_id",
        ),
        migrations.RemoveField(
            model_name="legopart",
            name="name",
        ),
        migrations.AddField(
            model_name="legopart",
            name="shape",
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to="lego.shape"
            ),
            preserve_default=False,
        ),
    ]
