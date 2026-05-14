import subprocess

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run the Tailwind CSS CLI"

    def add_arguments(self, parser):
        parser.add_argument(
            "subcommand",
            nargs="?",
            default="build",
            choices=["build", "watch"],
        )

    def handle(self, *args, **options):
        cmd = [
            "npx",
            "tailwindcss",
            "--input",
            "static/css/input.css",
            "--output",
            "static/css/main.css",
        ]
        if options["subcommand"] == "watch":
            cmd.append("--watch")
        elif options["subcommand"] == "build":
            cmd.append("--minify")
        result = subprocess.run(cmd, check=False)  # noqa: S603
        if result.returncode != 0:
            raise SystemExit(result.returncode)
