import pytest


@pytest.fixture(autouse=True)
def reset_structlog_contextvars():
    import structlog.contextvars

    structlog.contextvars.clear_contextvars()
    yield
    structlog.contextvars.clear_contextvars()
