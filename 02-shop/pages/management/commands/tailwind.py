import subprocess
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Build Tailwind CSS"

    def add_arguments(self, parser):  # type: ignore[override]
        parser.add_argument("action", choices=["build", "watch"], default="build", nargs="?")

    def handle(self, *args, **options):  # type: ignore[override]
        base_dir: Path = settings.BASE_DIR  # type: ignore[assignment]
        input_css = base_dir / "frontend" / "input.css"
        output_css = base_dir / "static" / "css" / "tailwind.css"
        output_css.parent.mkdir(parents=True, exist_ok=True)

        cmd = ["tailwindcss", "-i", str(input_css), "-o", str(output_css)]
        if options["action"] == "build":
            cmd.append("--minify")
        else:
            cmd.append("--watch")

        self.stdout.write(self.style.SUCCESS(f"Running: {' '.join(cmd)}"))
        subprocess.run(cmd, check=True)
