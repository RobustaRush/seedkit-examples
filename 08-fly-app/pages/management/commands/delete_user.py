from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = "Delete a user and all their data (GDPR erasure request)"

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int)

    def handle(self, *args, **options):
        with transaction.atomic():
            user = User.objects.get(pk=options["user_id"])
            username = user.get_username()
            user.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted user {username}"))
