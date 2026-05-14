from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()


class Command(BaseCommand):
    help = "Anonymise and delete personal data for a user (GDPR Article 17)"

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int)
        parser.add_argument("--confirm", action="store_true", required=True)

    def handle(self, *args, **options):
        try:
            user = User.objects.get(pk=options["user_id"])
        except User.DoesNotExist:
            raise CommandError(f"User {options['user_id']} not found")

        username = user.username
        user.email = ""
        user.first_name = ""
        user.last_name = ""
        user.is_active = False
        user.set_unusable_password()
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Anonymised user {username} (pk={user.pk})"))
