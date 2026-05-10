from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = "Delete a user and all their owned data (GDPR article 17 — right to erasure)."

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int)

    def handle(self, *args, **options):
        try:
            user = User.objects.get(pk=options["user_id"])
        except User.DoesNotExist:
            raise CommandError(f"User {options['user_id']} not found.")

        username = user.username
        with transaction.atomic():
            user.delete()

        self.stdout.write(self.style.SUCCESS(f"Deleted user {username} (id={options['user_id']})."))
