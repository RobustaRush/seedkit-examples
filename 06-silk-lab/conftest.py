from django.conf import settings


def pytest_configure():
    settings.DJANGO_SETTINGS_MODULE = "config.settings.local"


def pytest_sessionstart(session):
    if hasattr(settings, "MIDDLEWARE"):
        settings.MIDDLEWARE = [m for m in settings.MIDDLEWARE if "zeal" not in m.lower()]
