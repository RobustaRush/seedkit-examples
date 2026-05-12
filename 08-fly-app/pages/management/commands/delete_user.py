from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = "Delete all data for a user (GDPR right to erasure)"

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int)

    def handle(self, *args, **options):
        try:
            user = User.objects.get(pk=options["user_id"])
        except User.DoesNotExist:
            raise CommandError(f"User {options['user_id']} not found")

        email = user.email
        with transaction.atomic():
            user.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted user {email} (id={options['user_id']})"))
