from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = "Delete a user and all their data (GDPR Article 17)"

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int)

    def handle(self, *args, **options):
        try:
            user = User.objects.get(pk=options["user_id"])
        except User.DoesNotExist:
            raise CommandError(f"User {options['user_id']} does not exist") from None

        with transaction.atomic():
            user_repr = str(user)
            user.delete()

        self.stdout.write(self.style.SUCCESS(f"Deleted user {user_repr}"))
