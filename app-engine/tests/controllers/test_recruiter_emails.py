"""
# Recruiter Emails Controller Test

To run individually:

    nosetests -c nose.cfg tests/controllers/test_recruiter_emails.py
"""
from controllers.recruiter_emails import app as recruiter_emails_controller
from models.recruiter_email import RecruiterEmail

from tests.helper import (AppEngineControllerTest, TestEmail, parse_html)


class RecruiterEmailsControllerTest(AppEngineControllerTest):
    #
    # Tests
    #
    def test_expects_index_to_display_recruitments(self):
        # Arrange
        client = recruiter_emails_controller.test_client()
        mail_message = TestEmail.fixture('20160831_mkhurpe_fwd')
        recruitment = RecruiterEmail.from_inbound_handler(mail_message)

        # Assume
        self.assertFalse(recruitment.already_existed)
        self.assertEqual(RecruiterEmail.query().count(), 1)
        endpoint = '/admin/recruitments/'
        content_selector = 'div.recruiter-emails.index'
        table_selector = 'table.table'

        # Act
        response = client.get(endpoint, follow_redirects=False)
        html = parse_html(response.data)
        content = html.select_one(content_selector) if html else None
        table = content.select_one(table_selector) if content else None
        table_rows = table.select('tbody > tr') if table else []

        # Assert
        self.assertEqual(response.status_code, 200, html)
        self.assertIsNotNone(content)
        self.assertIsNotNone(table)
        self.assertEqual(content.h2.text.strip(), 'Recruiter Emails')
        self.assertEqual(len(table_rows), 1)
        self.assertEqual(table_rows[0].td.text.strip(), 'Tom Atwell <tatwell@gmail.com>')

    def test_expects_index_to_display_no_recruitments(self):
        # Arrange
        client = recruiter_emails_controller.test_client()

        # Assume
        self.assertEqual(RecruiterEmail.query().count(), 0)
        endpoint = '/admin/recruitments/'
        content_selector = 'div.recruiter-emails.index'
        table_selector = 'table.table'

        # Act
        response = client.get(endpoint, follow_redirects=False)
        html = parse_html(response.data)
        content = html.select_one(content_selector) if html else None
        table = content.select_one(table_selector) if content else None
        table_rows = table.select('tbody > tr') if table else []

        # Assert
        self.assertEqual(response.status_code, 200, html)
        self.assertEqual(len(table_rows), 1)
        self.assertEqual(table_rows[0].td.text.strip(), 'No emails found.')
