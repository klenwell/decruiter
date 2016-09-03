"""
# Mail Handler Test

To run individually:

    nosetests -c nose.cfg tests/handlers/test_mail_handler.py
"""
from webtest import TestApp

from mail_handler import app
from models.recruiter_email import RecruiterEmail

from tests.helper import (AppEngineTestCase, TestEmail, parse_html)


class RecruiterEmailsHandlerTest(AppEngineTestCase):
    #
    # Tests
    #
    def test_expect_handler_save_forwarded_recruiter_email(self):
        # Arrange
        client = TestApp(app)
        mail_message = TestEmail.fixture('online_recruiter_email_fwd')

        # Assume
        self.assertEqual(RecruiterEmail.query().count(), 0)
        endpoint = '/_ah/mail/test%40decruiter.appspotmail.com'
        body = mail_message.original.as_string()
        expected_checksum = 'b7776935b1fe86fb7046104bc50339a1'

        # Act
        response = client.post(endpoint, body)
        recruitments = RecruiterEmail.query().fetch()
        recruitment = recruitments[0] if recruitments else None

        # Assert
        self.assertEqual(response.status_code, 200, response)
        self.assertEqual(RecruiterEmail.query().count(), 1)
        self.assertIsNotNone(recruitment)
        self.assertEqual(recruitment.checksum, expected_checksum)
