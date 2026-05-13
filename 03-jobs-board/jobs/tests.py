from django.test import TestCase

from .models import JobPost


class JobPostModelTest(TestCase):
    def test_str(self):
        job = JobPost(title="Backend Engineer", company="Acme Corp")
        self.assertEqual(str(job), "Backend Engineer at Acme Corp")
