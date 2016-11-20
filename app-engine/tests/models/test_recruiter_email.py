"""
# RecruiterEmail Model Tests

To run individually:

    nosetests -c nose.cfg tests/models/test_recruiter_email.py
"""
from datetime import datetime

from models.recruiter_email import RecruiterEmail
from models.recruiter import Recruiter

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
        forwarder = 'forwarder@gmail.com'
        mail_message = TestEmail.fixture('20160831_mkhurpe_fwd', forwarder)

        # Assume
        expected_forwarder = 'The Recruitee <%s>' % (forwarder)
        expected_address = 'recruitment@decruiter.appspotmail.com'
        expected_subject_fwd = 'Fwd: CTF Engineering Lead - Menlo Park, CA'
        expected_checksum = 'd266496f821bfb50d2937f23679659de'
        expected_original_length = 17565
        expected_recruiter_name = 'Mahesh Khurpe'
        expected_recruiter_email = 'mahes.khurpe@xoriant.com'
        expected_sent_to = 'uRA sumA <%s>' % (forwarder)
        expected_sent_at = datetime(2016, 8, 31, 9, 41)
        expected_subject = 'CTF Engineering Lead - Menlo Park, CA'
        expected_plain_body_length = 2951
        expected_html_body_length = 10139

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
        forwarder = 'forwarder@gmail.com'
        mail_message = TestEmail.fixture('20160831_mkhurpe_fwd', forwarder)
        recruitment = RecruiterEmail.from_inbound_handler(mail_message)
        expected_checksum = 'd266496f821bfb50d2937f23679659de'

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

    def test_expects_recruiter_email_to_be_deleted(self):
        # Arrange
        mail_message = TestEmail.fixture('20160831_mkhurpe_fwd')
        recruitment = RecruiterEmail.from_inbound_handler(mail_message)
        recruiter = Recruiter.get_or_insert_by_recruitment(recruitment)
        recruitment.associate_recruiter(recruiter)

        # Assume
        self.assertEqual(RecruiterEmail.query().count(), 1)
        self.assertEqual(recruiter.email_count, 1)

        # Act
        recruiter = recruitment.delete()

        # Assert
        self.assertEqual(RecruiterEmail.query().count(), 0)
        self.assertEqual(recruiter.email_count, 0)

    def test_expects_to_extract_recruiter_name_and_email_from_from_line(self):
        # See Issue #7: https://github.com/klenwell/decruiter/issues/7
        # Assume
        from_line = 'Last, First <flast@example.com>'
        expected_name = 'First Last'
        expected_email = 'flast@example.com'

        # Act
        name, email = RecruiterEmail.from_line_to_name_and_email(from_line)

        # Assert
        self.assertEqual(name, expected_name)
        self.assertEqual(email, expected_email)

    def test_expects_to_extract_name_from_from_line_with_first_name_first(self):
        # Arrange
        cases = [
            # (from_line, expected_name)
            ('FIRST last <flast@example.com>', 'First Last'),
            ('Last, First (00100) <flast@example.com>', 'First Last'),
            ('Last, First <flast@example.com>', 'First Last'),
            ('Last, Middle, First <flast@example.com>', 'First Last')
        ]

        # Act
        for (from_line, expected_name) in cases:
            name, _ = RecruiterEmail.from_line_to_name_and_email(from_line)
            self.assertEqual(name, expected_name)
