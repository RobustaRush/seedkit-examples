import json

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Export all data for a user (GDPR subject access request)"

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int)

    def handle(self, *args, **options):
        user = User.objects.get(pk=options["user_id"])
        data = {
            "id": user.pk,
            "username": user.get_username(),
            "email": getattr(user, "email", ""),
            "date_joined": str(getattr(user, "date_joined", "")),
        }
        self.stdout.write(json.dumps(data, indent=2))
