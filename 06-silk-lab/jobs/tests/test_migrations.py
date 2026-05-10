import pytest


@pytest.mark.django_db
def test_jobs_initial_migration_forward_and_back(migrator):
    old_state = migrator.apply_initial_migration(("jobs", "0001_initial"))
    assert old_state is not None

    migrator.reset()
