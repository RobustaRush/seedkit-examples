from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = "Delete all data for a user (GDPR right to erasure)"

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int)

    def handle(self, *args, **options):
        try:
            user = User.objects.get(pk=options["user_id"])
        except User.DoesNotExist:
            raise CommandError(f"User {options['user_id']} does not exist")

        username = user.username
        with transaction.atomic():
            user.delete()
        self.stdout.write(f"Deleted user {username} (id={options['user_id']})")
