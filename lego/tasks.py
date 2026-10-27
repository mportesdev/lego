from django.tasks import task

from lego.images import _store_image


@task
def store_image(pk):
    _store_image(pk)
