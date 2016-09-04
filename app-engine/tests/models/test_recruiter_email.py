"""
# RecruiterEmail Model Tests

To run individually:

    nosetests -c nose.cfg tests/models/test_recruiter_email.py
"""
from datetime import datetime

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
        mail_message = TestEmail.fixture('20160831_mkhurpe_fwd')

        # Assume
        expected_forwarder = 'Tom Atwell <tatwell@gmail.com>'
        expected_address = 'recruitment@decruiter.appspotmail.com'
        expected_subject_fwd = 'Fwd: CTF Engineering Lead - Menlo Park, CA'
        expected_checksum = '706203edf87d7f035efc7e50c23282e2'
        expected_original_length = 17542
        expected_recruiter_name = 'Mahesh Khurpe'
        expected_recruiter_email = 'mahes.khurpe@xoriant.com'
        expected_sent_to = 'uRA sumA <tatwell@gmail.com>'
        expected_sent_at = datetime(2016, 8, 31, 9, 41)
        expected_subject = 'CTF Engineering Lead - Menlo Park, CA'
        expected_plain_body_length = 2945
        expected_html_body_length = 10133

        # Act
        recruitment = RecruiterEmail.from_inbound_handler(mail_message)

        # Assert
        self.assertEqual(recruitment.forwarding_address, expected_address)
        self.assertEqual(recruitment.forwarder, expected_forwarder)
        self.assertEqual(recruitment.forwarded_subject, expected_subject_fwd)
        self.assertEqual(recruitment.checksum, expected_checksum)
        self.assertEqual(recruitment.original_length, expected_original_length)
        self.assertEqual(recruitment.recruiter_name, expected_recruiter_name)
        self.assertEqual(recruitment.recruiter_email, expected_recruiter_email)
        self.assertEqual(recruitment.sent_to, expected_sent_to)
        self.assertEqual(recruitment.sent_at, expected_sent_at)
        self.assertEqual(recruitment.subject, expected_subject)
        self.assertEqual(len(recruitment.plain_body), expected_plain_body_length)
        self.assertEqual(len(recruitment.html_body), expected_html_body_length)

    def test_expects_duplicate_incoming_messages_to_be_saved_only_once(self):
        # Arrange
        mail_message = TestEmail.fixture('20160831_mkhurpe_fwd')
        recruitment = RecruiterEmail.from_inbound_handler(mail_message)
        expected_checksum = '706203edf87d7f035efc7e50c23282e2'

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
