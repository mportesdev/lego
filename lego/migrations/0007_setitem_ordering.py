# Generated by Django 5.1.3 on 2024-12-04 10:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("lego", "0006_legopart_unique_shape_color"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="setitem",
            options={"ordering": ["part__shape__name"]},
        ),
    ]
