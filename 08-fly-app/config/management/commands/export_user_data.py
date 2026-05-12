import json

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()


class Command(BaseCommand):
    help = "Export all data for a user as JSON (GDPR Article 20)"

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int)

    def handle(self, *args, **options):
        try:
            user = User.objects.get(pk=options["user_id"])
        except User.DoesNotExist:
            raise CommandError(f"User {options['user_id']} not found") from None

        data = {
            "id": user.pk,
            "username": getattr(user, "username", ""),
            "email": getattr(user, "email", ""),  # type: ignore[attr-defined]
            "date_joined": str(getattr(user, "date_joined", "")),  # type: ignore[attr-defined]
            "last_login": str(user.last_login),
        }
        self.stdout.write(json.dumps(data, indent=2))
