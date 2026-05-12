from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = "Delete a user and all their data (GDPR Article 17 — right to erasure)"

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int)
        parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")

    def handle(self, *args, **options):
        try:
            user = User.objects.get(pk=options["user_id"])
        except User.DoesNotExist:
            raise CommandError(f"User {options['user_id']} not found") from None

        if not options["yes"]:
            confirm = input(f"Delete user {getattr(user, 'email', user.pk)} (id={user.pk})? [y/N] ")  # type: ignore[attr-defined]
            if confirm.lower() != "y":
                self.stdout.write("Aborted.")
                return

        with transaction.atomic():
            user.delete()

        self.stdout.write(self.style.SUCCESS(f"User {options['user_id']} deleted."))
