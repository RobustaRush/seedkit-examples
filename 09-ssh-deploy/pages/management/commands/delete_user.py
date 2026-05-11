from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = "Delete a user and all owned data (GDPR Article 17 — right to erasure)."

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int)

    def handle(self, *args, **options):
        try:
            user = User.objects.get(pk=options["user_id"])
        except User.DoesNotExist as exc:
            raise CommandError(f"User {options['user_id']} does not exist.") from exc

        with transaction.atomic():
            username = user.username
            user.delete()

        self.stdout.write(
            self.style.SUCCESS(f"Deleted user '{username}' (pk={options['user_id']}).")
        )
