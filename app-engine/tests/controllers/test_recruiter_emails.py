"""
# Recruiter Emails Controller Test

To run individually:

    nosetests -c nose.cfg tests/controllers/test_recruiter_emails.py
"""
from controllers.recruiter_emails import app as recruiter_emails_controller
from models.recruiter_email import RecruiterEmail
from models.recruiter import Recruiter

from tests.helper import (AppEngineControllerTest, TestEmail,
                          parse_html, redirect_path)


class RecruiterEmailsControllerTest(AppEngineControllerTest):
    #
    # Tests
    #
    def test_expects_index_to_display_recruitments(self):
        # Arrange
        client = recruiter_emails_controller.test_client()
        forwarder = 'forwarder@gmail.com'
        mail_message = TestEmail.fixture('20160831_mkhurpe_fwd', forwarder)
        recruitment = RecruiterEmail.from_inbound_handler(mail_message)

        # Assume
        self.assertFalse(recruitment.already_existed)
        self.assertEqual(RecruiterEmail.query().count(), 1)
        endpoint = '/admin/recruitments/'
        content_selector = 'div.recruiter-emails.index'
        table_selector = 'table.table'
        expected_cell_value = 'Mahesh Khurpe'

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
        self.assertEqual(table_rows[0].td.text.strip(), expected_cell_value)

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
        self.assertEqual(table_rows[0].td.text.strip(), 'No recruitments found.')

    def test_expects_recruitment_to_be_reparsed(self):
        # Arrange
        client = recruiter_emails_controller.test_client()
        mail_message = TestEmail.fixture('20160831_mkhurpe_fwd')
        recruitment = RecruiterEmail.from_inbound_handler(mail_message)

        # Assume
        self.assertIsNone(recruitment.recruiter)
        endpoint = '/admin/recruitment/reparse/'
        form_data = dict(
            csrf_token='mock',
            recruitment_id=recruitment.public_id,
        )
        expected_redirect = '/admin/recruitment/%s/' % (recruitment.public_id)
        expected_recruiter_email = 'mahes.khurpe@xoriant.com'

        # Act
        response = client.post(endpoint, data=form_data, follow_redirects=False)
        recruitment = RecruiterEmail.read(recruitment.public_id)

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertEqual(redirect_path(response), expected_redirect)
        self.assertIsNotNone(recruitment.recruiter)
        self.assertEqual(recruitment.recruiter.email, expected_recruiter_email)

    def test_expects_recruitment_to_be_deleted(self):
        # Arrange
        client = recruiter_emails_controller.test_client()
        mail_message = TestEmail.fixture('20160831_mkhurpe_fwd')
        recruitment = RecruiterEmail.from_inbound_handler(mail_message)
        recruiter = Recruiter.get_or_insert_by_recruitment(recruitment)
        recruitment.associate_recruiter(recruiter)

        # Assume
        self.assertEqual(RecruiterEmail.query().count(), 1)
        self.assertEqual(recruiter.email_count, 1)
        endpoint = '/admin/recruitment/delete/'
        form_data = dict(
            csrf_token='mock',
            recruitment_id=recruitment.public_id,
        )
        expected_redirect = '/admin/recruitments/'

        # Act
        response = client.post(endpoint, data=form_data, follow_redirects=False)
        recruitment = RecruiterEmail.read(recruitment.public_id)

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertEqual(redirect_path(response), expected_redirect)
        self.assertEqual(RecruiterEmail.query().count(), 0)
        self.assertEqual(recruiter.email_count, 0)
