import structlog
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

User = get_user_model()
log = structlog.get_logger(__name__)


class Command(BaseCommand):
    help = "Delete all data for a user (GDPR Article 17)"

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int)
        parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")

    def handle(self, *args, **options):
        try:
            user = User.objects.get(pk=options["user_id"])
        except User.DoesNotExist:
            raise CommandError(f"User {options["user_id"]} not found") from None

        if not options["yes"]:
            confirm = input(f"Delete user {user.username} ({user.email})? [y/N] ")
            if confirm.lower() != "y":
                self.stdout.write("Aborted.")
                return

        with transaction.atomic():
            user_id = user.pk
            username = user.username
            user.delete()
            log.info("user_deleted", user_id=user_id, username=username)

        self.stdout.write(self.style.SUCCESS(f"Deleted user {username} (id={user_id})"))
