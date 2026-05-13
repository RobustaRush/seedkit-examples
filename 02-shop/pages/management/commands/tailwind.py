import subprocess
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Tailwind CSS operations (build / watch / install)"

    def add_arguments(self, parser):
        parser.add_argument("subcommand", choices=["build", "watch", "install"])

    def handle(self, *args, **options):
        subcommand = options["subcommand"]
        base = Path(__file__).resolve().parents[3]  # project root

        if subcommand == "install":
            result = subprocess.run(["npm", "install"], cwd=base)
        elif subcommand == "build":
            result = subprocess.run(
                [
                    "npx",
                    "--yes",
                    "@tailwindcss/cli",
                    "-i",
                    "frontend/input.css",
                    "-o",
                    "static/css/tailwind.css",
                    "--minify",
                ],
                cwd=base,
            )
        elif subcommand == "watch":
            result = subprocess.run(
                [
                    "npx",
                    "--yes",
                    "@tailwindcss/cli",
                    "-i",
                    "frontend/input.css",
                    "-o",
                    "static/css/tailwind.css",
                    "--watch",
                ],
                cwd=base,
            )
        else:
            raise CommandError(f"Unknown subcommand: {subcommand}")

        if result.returncode != 0:
            raise CommandError(f"tailwind {subcommand} failed (exit {result.returncode})")

        self.stdout.write(self.style.SUCCESS(f"tailwind {subcommand} done"))
