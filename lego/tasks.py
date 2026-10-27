from django.tasks import task

from lego.images import store_image_for_pk


@task
def store_image(pk):
    store_image_for_pk(pk)
