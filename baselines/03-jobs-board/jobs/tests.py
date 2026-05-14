from django.test import TestCase

from .tasks import send_daily_digest, send_job_notification


class TasksTest(TestCase):
    def test_send_job_notification(self):
        result = send_job_notification(42)
        self.assertIn("42", result)

    def test_send_daily_digest(self):
        result = send_daily_digest()
        self.assertEqual(result, "daily digest sent")
