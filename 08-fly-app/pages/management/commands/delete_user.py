from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = "Delete a user and all owned data (GDPR Art. 17)"

    def add_arguments(self, parser):  # type: ignore[override]
        parser.add_argument("user_id", type=int)

    def handle(self, *args, **options):  # type: ignore[override]
        try:
            user = User.objects.get(pk=options["user_id"])
        except User.DoesNotExist:
            raise CommandError(f"User {options['user_id']} not found")

        with transaction.atomic():
            user_repr = str(user)
            user.delete()
        self.stdout.write(f"Deleted user {user_repr} (id={options['user_id']})")
