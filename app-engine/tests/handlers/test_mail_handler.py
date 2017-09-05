"""
# Mail Handler Test

To run individually:

    nosetests -c nose.cfg tests/handlers/test_mail_handler.py
"""
from webtest import TestApp
from mock import patch
from urllib import quote_plus

from mail_handler import app, HandlerAuthorizationError
from models.recruiter_email import RecruiterEmail
from models.recruiter import Recruiter

from tests.helper import (AppEngineTestCase, TestEmail, parse_html)


# Test Forwarders
authorized_forwarder = 'forwarder@gmail.com'
unauthorized_forwarder = 'unauthorized@gmail.com'
reply_trigger_email = 'reply@foo.appspotmail.com'


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

    @patch("mail_handler.AUTHORIZED_FORWARDERS", [authorized_forwarder])
    def test_expects_handler_to_set_recruiter_name_to_email_address_when_name_absent(self):
        # Previously was leaving field blank.
        # See Issue #5: https://github.com/klenwell/decruiter/issues/5
        # Arrange
        client = TestApp(app)
        mail_message = TestEmail.fixture('20160901_no_recruiter_name_fwd', authorized_forwarder)

        # Assume
        self.assertEqual(RecruiterEmail.query().count(), 0)
        self.assertEqual(Recruiter.query().count(), 0)
        endpoint = '/_ah/mail/test%40decruiter.appspotmail.com'
        body = mail_message.original.as_string()
        expected_recruiter_name = 'Charan Kumar'
        expected_recruiter_email = 'charan.kumar@elitebizconsulting.com'

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
        self.assertEqual(recruitment.recruiter.email, expected_recruiter_email)
        self.assertEqual(recruitment.recruiter.name, expected_recruiter_name)

    @patch("mail_handler.AUTHORIZED_FORWARDERS", [authorized_forwarder])
    @patch("mail_handler.AUTOMATED_REPLY_TRIGGER_EMAIL", reply_trigger_email)
    def test_expects_to_send_automated_reply(self):
        # NOTE: mail_handler.AUTOMATED_REPLY_TRIGGER_EMAIL must be patched to match
        # recipient in email fixture file.
        # Arrange
        client = TestApp(app)
        mail_stub = self.initMailStub()
        mail_message = TestEmail.fixture('20160831_mkhurpe_fwd', authorized_forwarder)
        endpoint = '/_ah/mail/%s' % (quote_plus(reply_trigger_email))

        # Assume
        self.assertEqual(RecruiterEmail.query().count(), 0)
        self.assertEqual(Recruiter.query().count(), 0)
        body = mail_message.original.as_string()
        expected_recruiter_name = 'Mahesh Khurpe'
        expected_recruiter_email = 'mahes.khurpe@xoriant.com'

        # Act
        with patch('mail_handler.logging.info') as mock_logger:
            response = client.post(endpoint, body)
            messages = mail_stub.get_sent_messages()
            last_log_message = mock_logger.call_args_list[-1]

        # Assert
        self.assertEqual(response.status_code, 200, response)
        self.assertEqual(RecruiterEmail.query().count(), 1)
        self.assertEqual(Recruiter.query().count(), 1)
        self.assertEqual(mock_logger.call_count, 3)
        self.assertIn('Automated reply sent', str(last_log_message))
        self.assertEqual(len(messages), 1)

    def test_expects_not_to_send_automated_reply(self):
        pass
