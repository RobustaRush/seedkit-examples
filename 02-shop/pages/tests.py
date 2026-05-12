from django.test import TestCase


class IndexViewTest(TestCase):
    def test_index_ok(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
