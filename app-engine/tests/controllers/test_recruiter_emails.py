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

    def test_expects_recruitment_to_display_plain_body_html_body_and_original_email(self):
        # Arrange
        client = recruiter_emails_controller.test_client()
        forwarder = 'forwarder@gmail.com'
        mail_message = TestEmail.fixture('20160831_mkhurpe_fwd', forwarder)
        recruitment = RecruiterEmail.from_inbound_handler(mail_message)
        recruiter = Recruiter.get_or_insert_by_recruitment(recruitment)
        recruitment.associate_recruiter(recruiter)

        # Assume
        endpoint = '/admin/recruitment/%s/' % (recruitment.public_id)
        content_selector = 'div.recruiter-email.show'
        subject_selector = 'dd.subject'
        plain_body_selector = 'div#recruitment-body-plain pre'
        html_body_selector = 'div#recruitment-body-html'
        original_selector = 'div#recruitment-original pre'

        # Act
        response = client.get(endpoint, follow_redirects=False)
        html = parse_html(response.data)
        content = html.select_one(content_selector) if html else None
        subject = content.select_one(subject_selector) if content else None
        plain_body = content.select_one(plain_body_selector) if content else None
        html_body = content.select_one(html_body_selector) if content else None
        original = content.select_one(original_selector) if content else None

        # Assert
        self.assertEqual(response.status_code, 200, html)
        self.assertIsNotNone(content)
        self.assertIsNotNone(subject)
        self.assertIsNotNone(plain_body)
        self.assertIsNotNone(html_body)
        self.assertIsNotNone(original)
        self.assertEqual(subject.text.strip(), recruitment.subject)
        self.assertEqual(plain_body.text.strip(), recruitment.plain_body)
        self.assertEqual(html_body.decode_contents(formatter="html").strip()[:100],
                         recruitment.html_body[:100])
        self.assertEqual(original.text.strip(), recruitment.original)

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

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertEqual(redirect_path(response), expected_redirect)
        self.assertEqual(RecruiterEmail.query().count(), 0)
        self.assertEqual(recruiter.email_count, 0)

    def test_expects_recruitment_to_be_deleted_even_when_not_associated_with_recruiter(self):
        # This was Issue #4: https://github.com/klenwell/decruiter/issues/4
        # Arrange
        client = recruiter_emails_controller.test_client()
        mail_message = TestEmail.fixture('20160831_mkhurpe_fwd')
        recruitment = RecruiterEmail.from_inbound_handler(mail_message)

        # Assume
        self.assertEqual(RecruiterEmail.query().count(), 1)
        endpoint = '/admin/recruitment/delete/'
        form_data = dict(
            csrf_token='mock',
            recruitment_id=recruitment.public_id,
        )
        expected_redirect = '/admin/recruitments/'

        # Act
        response = client.post(endpoint, data=form_data, follow_redirects=False)

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertEqual(redirect_path(response), expected_redirect)
        self.assertEqual(RecruiterEmail.query().count(), 0)

    def test_expects_400_status_when_csrf_token_is_missing(self):
        # Arrange
        client = recruiter_emails_controller.test_client()
        mail_message = TestEmail.fixture('20160831_mkhurpe_fwd')
        recruitment = RecruiterEmail.from_inbound_handler(mail_message)

        # Assume
        self.assertIsNone(recruitment.recruiter)
        endpoint = '/admin/recruitment/reparse/'
        form_data = dict(recruitment_id=recruitment.public_id,)
        self.assertIsNone(form_data.get('csrf_token'))
        expected_header = '400: Bad Request'
        expected_error_message = 'The CSRF token is missing.'

        # Act
        response = client.post(endpoint, data=form_data, follow_redirects=False)
        html = parse_html(response.data)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(html.h2.text.strip(), expected_header)
        self.assertEqual(html.h4.text.strip(), expected_error_message)
