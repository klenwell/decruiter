"""
# RecruiterEmail Model Tests

To run individually:

    nosetests -c nose.cfg tests/models/test_recruiter_email.py
"""
from models.recruiter_email import RecruiterEmail

from tests.helper import AppEngineModelTest, TestEmail


#
# Test Case
#
class RecruiterEmailModelTest(AppEngineModelTest):

    def test_expects_from_handler_to_save_record(self):
        # Arrange
        mail_message = TestEmail.fixture('online_recruiter_email_fwd')

        # Act
        recruitment = RecruiterEmail.from_inbound_handler(mail_message)

        # Assert
        self.assertEqual(recruitment.forwarding_address, 'Tom Atwell <klenwell@gmail.com>')
        self.assertEqual(recruitment.forwarder, 'Tom Atwell <tatwell@gmail.com>')
        self.assertEqual(len(recruitment.original), 18741)

    def test_expects_to_create_model_instance(self):
        # Act
        recruitment = RecruiterEmail()

        # Assert
        self.assertIsInstance(recruitment, RecruiterEmail)
