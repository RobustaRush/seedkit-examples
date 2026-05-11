from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = "Permanently delete a user and all their owned data (GDPR erasure)."

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int)
        parser.add_argument("--confirm", action="store_true", required=True)

    def handle(self, *args, **options):
        try:
            user = User.objects.get(pk=options["user_id"])
        except User.DoesNotExist:
            raise CommandError(f"User {options['user_id']} does not exist.") from None

        username = user.get_username()
        with transaction.atomic():
            user.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted user {username} (pk={options['user_id']})."))
