import factory
from factory.django import DjangoModelFactory


class ShapeFactory(DjangoModelFactory):
    class Meta:
        model = "lego.Shape"

    lego_id = factory.Sequence(lambda n: f"{n:04}")
    name = factory.Sequence(lambda n: f"Test Shape {n}")


class ColorFactory(DjangoModelFactory):
    class Meta:
        model = "lego.Color"

    name = factory.Sequence(lambda n: f"Test Color {n}")


class ImageFactory(DjangoModelFactory):
    class Meta:
        model = "lego.Image"

    path = factory.Sequence(lambda n: f"/lego/img/test{n:04}.webp")
    origin_url = factory.Sequence(lambda n: f"test://{n}.jpg")


class LegoPartFactory(DjangoModelFactory):
    class Meta:
        model = "lego.LegoPart"

    shape = factory.SubFactory(ShapeFactory)
    color = factory.SubFactory(ColorFactory)
    image = factory.SubFactory(ImageFactory)
