import django
from django.conf import settings  # noqa: F401 — imported to trigger settings load

# pytest-django picks up DJANGO_SETTINGS_MODULE from pyproject.toml [tool.pytest.ini_options].
# This file exists as the entry point for project-specific fixtures.
