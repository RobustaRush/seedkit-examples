"""GDPR: export all data held for a user as JSON."""
import json

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()


class Command(BaseCommand):
    help = "Export all personal data for a user (GDPR Art. 20)"

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int, help="Primary key of the user")
        parser.add_argument("--output", default="-", help="Output file path (default: stdout)")

    def handle(self, *args, **options):
        try:
            user = User.objects.get(pk=options["user_id"])
        except User.DoesNotExist:
            raise CommandError(f"User {options['user_id']} not found")

        data = {
            "id": user.pk,
            "username": user.username,
            "email": user.email,
            "date_joined": user.date_joined.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
        }

        payload = json.dumps(data, indent=2)
        if options["output"] == "-":
            self.stdout.write(payload)
        else:
            with open(options["output"], "w") as f:
                f.write(payload)
            self.stdout.write(self.style.SUCCESS(f"Exported to {options['output']}"))
