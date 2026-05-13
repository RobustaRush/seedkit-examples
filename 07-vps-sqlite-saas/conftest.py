import django
import pytest


@pytest.fixture(autouse=True)
def reset_structlog_contextvars():
    import structlog
    structlog.contextvars.clear_contextvars()
    yield
    structlog.contextvars.clear_contextvars()
