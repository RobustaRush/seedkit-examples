import json

from django.contrib.auth import get_user_model
from django.core import serializers
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Export all data for a user as JSON (GDPR Article 20)."

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int)

    def handle(self, *args, user_id, **opts):
        user = get_user_model().objects.get(pk=user_id)
        data = json.loads(serializers.serialize("json", [user]))
        self.stdout.write(json.dumps(data, indent=2))
