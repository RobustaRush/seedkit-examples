import json

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()


class Command(BaseCommand):
    help = "Export all personal data for a user (GDPR Art. 20)"

    def add_arguments(self, parser):  # type: ignore[override]
        parser.add_argument("user_id", type=int)

    def handle(self, *args, **options):  # type: ignore[override]
        try:
            user = User.objects.get(pk=options["user_id"])
        except User.DoesNotExist:
            raise CommandError(f"User {options['user_id']} not found")

        data = {
            "id": user.pk,
            "username": user.username,
            "email": user.email,
            "date_joined": str(user.date_joined),
            "last_login": str(user.last_login),
        }
        self.stdout.write(json.dumps(data, indent=2))
