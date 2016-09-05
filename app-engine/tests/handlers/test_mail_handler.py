"""
# Mail Handler Test

To run individually:

    nosetests -c nose.cfg tests/handlers/test_mail_handler.py
"""
from webtest import TestApp

from mail_handler import app
from models.recruiter_email import RecruiterEmail
from models.recruiter import Recruiter

from tests.helper import (AppEngineTestCase, TestEmail, parse_html)


class RecruiterEmailsHandlerTest(AppEngineTestCase):
    #
    # Tests
    #
    def test_expects_handler_to_save_forwarded_recruiter_email(self):
        # Arrange
        client = TestApp(app)
        mail_message = TestEmail.fixture('20160831_mkhurpe_fwd')

        # Assume
        self.assertEqual(RecruiterEmail.query().count(), 0)
        self.assertEqual(Recruiter.query().count(), 0)
        endpoint = '/_ah/mail/test%40decruiter.appspotmail.com'
        body = mail_message.original.as_string()
        expected_checksum = '706203edf87d7f035efc7e50c23282e2'
        expected_recruiter_name = 'Mahesh Khurpe'
        expected_recruiter_email = 'mahes.khurpe@xoriant.com'

        # Act
        response = client.post(endpoint, body)
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
