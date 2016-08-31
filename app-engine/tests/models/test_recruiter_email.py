"""
# RecruiterEmail Model Tests

To run individually:

    nosetests -c nose.cfg tests/models/test_recruiter_email.py
"""
from models.recruiter_email import RecruiterEmail

from tests.helper import AppEngineModelTest


#
# Test Case
#
class RecruiterEmailModelTest(AppEngineModelTest):

    def test_expects_to_create_model_instance(self):
        # Arrange
        raw_email_text = 'Imagine this were a real recruiter email.'

        # Act
        recruitment = RecruiterEmail(raw=raw_email_text)

        # Assert
        self.assertIsInstance(recruitment, RecruiterEmail)
        self.assertEqual(recruitment.raw, raw_email_text)
