"""
# Mail Handler Test

To run individually:

    nosetests -c nose.cfg tests/handlers/test_mail_handler.py
"""
from webtest import TestApp
from mock import patch

from mail_handler import app, HandlerAuthorizationError
from models.recruiter_email import RecruiterEmail
from models.recruiter import Recruiter

from tests.helper import (AppEngineTestCase, TestEmail, parse_html)


# Test Forwarders
authorized_forwarder = 'forwarder@gmail.com'
unauthorized_forwarder = 'unauthorized@gmail.com'


class RecruiterEmailsHandlerTest(AppEngineTestCase):
    #
    # Tests
    #
    @patch("mail_handler.AUTHORIZED_FORWARDERS", [authorized_forwarder])
    def test_expects_handler_to_save_forwarded_recruiter_email(self):
        # Arrange
        client = TestApp(app)
        mail_message = TestEmail.fixture('20160831_mkhurpe_fwd', authorized_forwarder)

        # Assume
        self.assertEqual(RecruiterEmail.query().count(), 0)
        self.assertEqual(Recruiter.query().count(), 0)
        endpoint = '/_ah/mail/test%40decruiter.appspotmail.com'
        body = mail_message.original.as_string()
        expected_checksum = 'd266496f821bfb50d2937f23679659de'
        expected_recruiter_name = 'Mahesh Khurpe'
        expected_recruiter_email = 'mahes.khurpe@xoriant.com'

        # Act
        response = client.post(endpoint, body, expect_errors=True)
        recruitments = RecruiterEmail.query().fetch()
        recruitment = recruitments[0] if recruitments else None

        # Assert
        self.assertEqual(response.status_code, 200, response)
        self.assertEqual(RecruiterEmail.query().count(), 1)
        self.assertEqual(Recruiter.query().count(), 1)
        self.assertIsNotNone(recruitment)
        self.assertIsNotNone(recruitment.recruiter)
        self.assertEqual(recruitment.checksum, expected_checksum)
        self.assertEqual(recruitment.recruiter.email, expected_recruiter_email)
        self.assertEqual(recruitment.recruiter.name, expected_recruiter_name)

    @patch("mail_handler.AUTHORIZED_FORWARDERS", [authorized_forwarder])
    def test_expects_handler_not_to_save_previously_forwarded_recruiter_email(self):
        # Arrange
        client = TestApp(app)
        mail_message = TestEmail.fixture('20160831_mkhurpe_fwd', authorized_forwarder)
        recruitment = RecruiterEmail.from_inbound_handler(mail_message)
        recruiter = Recruiter.get_or_insert_by_recruitment(recruitment)
        recruitment.associate_recruiter(recruiter)

        # Assume
        self.assertEqual(RecruiterEmail.query().count(), 1)
        self.assertEqual(Recruiter.query().count(), 1)
        endpoint = '/_ah/mail/test%40decruiter.appspotmail.com'
        body = mail_message.original.as_string()

        # Act
        response = client.post(endpoint, body, expect_errors=True)
        recruitments = RecruiterEmail.query().fetch()

        # Assert
        self.assertEqual(response.status_code, 200, response)
        self.assertEqual(len(recruitments), 1)
        self.assertEqual(recruitments[0].key, recruitment.key)

    @patch("mail_handler.AUTHORIZED_FORWARDERS", [unauthorized_forwarder])
    def test_expects_authorization_error(self):
        # Notice: patched forwarder in AUTHORIZED_FORWARDERS and forwarder injected into
        # mail message do not match.
        # Arrange
        client = TestApp(app)
        mail_message = TestEmail.fixture('20160831_unauthorized_fwd', authorized_forwarder)

        # Assume
        self.assertEqual(RecruiterEmail.query().count(), 0)
        self.assertEqual(Recruiter.query().count(), 0)
        endpoint = '/_ah/mail/test%40decruiter.appspotmail.com'
        body = mail_message.original.as_string()

        # Act / Assert
        response = client.post(endpoint, body, expect_errors=True)

        # Assert
        self.assertEqual(response.status_code, 500, response)
        self.assertEqual(RecruiterEmail.query().count(), 0)
        self.assertEqual(Recruiter.query().count(), 0)
