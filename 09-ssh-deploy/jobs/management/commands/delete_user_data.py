"""GDPR: delete a user account and their personal data."""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()


class Command(BaseCommand):
    help = "Delete a user and all their personal data (GDPR Art. 17)"

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int, help="Primary key of the user")
        parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")

    def handle(self, *args, **options):
        try:
            user = User.objects.get(pk=options["user_id"])
        except User.DoesNotExist:
            raise CommandError(f"User {options['user_id']} not found")

        if not options["yes"]:
            confirm = input(f"Delete user '{user.username}' (pk={user.pk})? [y/N] ")
            if confirm.lower() != "y":
                self.stdout.write("Aborted.")
                return

        user.delete()
        self.stdout.write(self.style.SUCCESS(f"User {options['user_id']} deleted."))
