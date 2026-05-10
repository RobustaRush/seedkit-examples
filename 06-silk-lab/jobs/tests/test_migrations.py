import pytest


@pytest.mark.django_db
def test_jobs_initial_migration_forward_and_back(migrator):
    # Apply all migrations up to (but not including) jobs 0001_initial.
    migrator.apply_initial_migration(("jobs", "0001_initial"))

    # Apply the migration under test.
    new_state = migrator.apply_tested_migration(("jobs", "0001_initial"))

    EmailJob = new_state.apps.get_model("jobs", "EmailJob")
    assert EmailJob.objects.count() == 0

    # Restore the full migration state (verifies no conflicts).
    migrator.reset()
