from django.contrib.auth.models import User
from django.core.management import call_command

if not User.objects.filter(is_superuser=True):
    call_command("createsuperuser", "--no-input", username="admin", email="")
