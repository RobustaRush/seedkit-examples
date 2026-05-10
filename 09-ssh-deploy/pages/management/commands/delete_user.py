from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = "Delete all personal data for a user (GDPR Article 17)."

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int)

    def handle(self, *args, **options):
        try:
            user = User.objects.get(pk=options["user_id"])
        except User.DoesNotExist as exc:
            raise CommandError(f"User {options['user_id']} does not exist.") from exc
        with transaction.atomic():
            user_repr = f"id={user.pk} email={user.email}"
            user.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted user {user_repr}"))
