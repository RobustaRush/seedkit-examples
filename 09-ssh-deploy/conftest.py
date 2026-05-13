import pytest
import structlog.contextvars


@pytest.fixture(autouse=True)
def _reset_structlog_context():
    structlog.contextvars.clear_contextvars()
    yield
    structlog.contextvars.clear_contextvars()
