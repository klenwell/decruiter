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
    def test_expects_to_create_model_instance(self):
        # Act
        recruitment = RecruiterEmail()

        # Assert
        self.assertIsInstance(recruitment, RecruiterEmail)

    def test_expects_record_to_be_saved_by_from_inbound_handler(self):
        # Arrange
        mail_message = TestEmail.fixture('online_recruiter_email_fwd')

        # Assume
        expected_forwarder = 'Tom Atwell <tatwell@gmail.com>'
        expected_address = 'Tom Atwell <klenwell@gmail.com>'
        expected_subject = "Fwd: Need:: Python Developer (IA-Iowa/Des Moinses, " \
                           "6-12 Months )\n Skype then F2F hire"
        expected_checksum = 'b7776935b1fe86fb7046104bc50339a1'

        # Act
        recruitment = RecruiterEmail.from_inbound_handler(mail_message)

        # Assert
        self.assertEqual(recruitment.forwarding_address, expected_address)
        self.assertEqual(recruitment.forwarder, expected_forwarder)
        self.assertEqual(recruitment.forwarded_subject, expected_subject)
        self.assertEqual(recruitment.checksum, expected_checksum)
        self.assertEqual(len(recruitment.original), 18741)

    def test_expects_duplicate_incoming_messages_to_be_saved_only_once(self):
        # Arrange
        mail_message = TestEmail.fixture('online_recruiter_email_fwd')
        recruitment = RecruiterEmail.from_inbound_handler(mail_message)
        expected_checksum = 'b7776935b1fe86fb7046104bc50339a1'

        # Assume
        self.assertEqual(RecruiterEmail.query().count(), 1)
        self.assertEqual(recruitment.checksum, expected_checksum)
        self.assertFalse(recruitment.already_existed)

        # Act
        duplicate = RecruiterEmail.from_inbound_handler(mail_message)

        # Assert
        self.assertEqual(RecruiterEmail.query().count(), 1)
        self.assertEqual(recruitment.checksum, duplicate.checksum)
        self.assertTrue(duplicate.already_existed)
