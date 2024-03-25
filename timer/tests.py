from django.test import TestCase

from .models import generate_session_id

class UtilsTests(TestCase):
    def test_generate_session_id(self):
        self.assertEqual(generate_session_id(), 100)
