"""
# Recruiters Controller Test

To run individually:

    nosetests -c nose.cfg tests/controllers/test_recruiters.py
"""
from controllers.recruiters import app as recruiters_controller
from models.recruiter_email import RecruiterEmail
from models.recruiter import Recruiter

from tests.helper import (AppEngineControllerTest, TestEmail,
                          parse_html, redirect_path)


class RecruiterEmailsControllerTest(AppEngineControllerTest):
    #
    # Harness
    #
    def insertRecruiter(self):
        mail_message = TestEmail.fixture()
        recruitment = RecruiterEmail.from_inbound_handler(mail_message)
        recruiter = Recruiter.get_or_insert_by_recruitment(recruitment)
        recruitment.associate_recruiter(recruiter)
        return recruiter

    #
    # Tests
    #
    def test_expects_index_to_display_recruiters(self):
        # Arrange
        client = recruiters_controller.test_client()
        recruiter = self.insertRecruiter()

        # Assume
        self.assertEqual(Recruiter.query().count(), 1)
        self.assertEqual(recruiter.email_count, 1)
        endpoint = '/admin/recruiters/'
        content_selector = 'div.recruiters.index'
        table_selector = 'table.table'
        expected_recruiter_name = 'Harold Kumar'
        paginator_selector = 'ul.pagination'

        # Act
        response = client.get(endpoint, follow_redirects=False)
        html = parse_html(response.data)
        content = html.select_one(content_selector) if html else None
        table = content.select_one(table_selector) if content else None
        table_rows = table.select('tbody > tr') if table else []
        paginator = content.select_one(paginator_selector) if content else None

        # Assert
        self.assertEqual(response.status_code, 200, html)
        self.assertIsNotNone(content)
        self.assertIsNotNone(table)
        self.assertIsNotNone(paginator)
        self.assertEqual(content.h2.text.strip(), 'Recruiters')
        self.assertEqual(len(table_rows), 1)
        self.assertEqual(table_rows[0].td.text.strip(), expected_recruiter_name)

    def test_expects_to_add_or_remove_recruiters_from_mailing_lists_in_index_view(self):
        # Arrange
        client = recruiters_controller.test_client()
        recruiter = self.insertRecruiter()

        # Assume
        self.assertEqual(Recruiter.query().count(), 1)
        self.assertEqual(recruiter.email_count, 1)
        endpoint = '/admin/recruiters/'
        content_selector = 'div.recruiters.index'
        cell_selector = 'td.mailing-list'
        button_group_selector = 'div.btn-group'

        # Act
        response = client.get(endpoint, follow_redirects=False)
        html = parse_html(response.data)
        content = html.select_one(content_selector) if html else None
        mailing_list_cell = content.select_one(cell_selector) if content else None
        mailing_list_button_group = mailing_list_cell.select_one(button_group_selector) \
            if mailing_list_cell else None

        # Assert
        self.assertEqual(response.status_code, 200, html)
        self.assertIsNotNone(content)
        self.assertIsNotNone(mailing_list_cell)
        self.assertIsNotNone(mailing_list_button_group)

    def test_expects_recruiter_to_be_displayed_with_recruitments(self):
        # Arrange
        client = recruiters_controller.test_client()
        recruiter = self.insertRecruiter()

        # Assume
        self.assertEqual(Recruiter.query().count(), 1)
        self.assertEqual(recruiter.email_count, 1)
        endpoint = '/admin/recruiter/%s/' % (recruiter.public_id)
        content_selector = 'div.recruiter.show'
        name_selector = 'div.recruiter-data h2.name'
        recruiters_selector = 'div.recruitments table.table'
        expected_recruiter_name = 'Harold Kumar'
        expected_column_value = '2016-08-31 09:41:00'

        # Act
        response = client.get(endpoint, follow_redirects=False)
        html = parse_html(response.data)
        content = html.select_one(content_selector) if html else None
        recruiter_name = content.select_one(name_selector) if content else None
        recruiters_table = content.select_one(recruiters_selector) if content else None
        table_rows = recruiters_table.select('tbody > tr') if recruiters_table else []

        # Assert
        self.assertEqual(response.status_code, 200, html)
        self.assertIsNotNone(content)
        self.assertIsNotNone(recruiter_name)
        self.assertIsNotNone(recruiters_table)
        self.assertEqual(recruiter_name.text.strip(), expected_recruiter_name)
        self.assertEqual(len(table_rows), 1)
        self.assertEqual(table_rows[0].td.text.strip(), expected_column_value)

    def test_expects_admin_to_edit_recruiter(self):
        # Arrange
        client = recruiters_controller.test_client()
        recruiter = self.insertRecruiter()

        # Assume
        self.assertEqual(Recruiter.query().count(), 1)
        self.assertEqual(recruiter.email_count, 1)
        endpoint = '/admin/recruiter/%s/edit/' % (recruiter.public_id)
        content_selector = 'div.recruiter.edit'
        form_selector = 'form#recruiter-edit'
        mailing_list_selector = 'div.form-group label.mailing-list'

        # Act
        response = client.get(endpoint, follow_redirects=False)
        html = parse_html(response.data)
        content = html.select_one(content_selector) if html else None
        form = content.select_one(form_selector) if content else None
        mailing_list_group = content.select_one(mailing_list_selector) if content else None

        # Assert
        self.assertEqual(response.status_code, 200, html)
        self.assertIsNotNone(content)
        self.assertIsNotNone(form)
        self.assertIsNotNone(mailing_list_group)

    def test_expects_recruiter_to_be_updated_and_synced_with_recruitments(self):
        # Arrange
        client = recruiters_controller.test_client()
        recruiter = self.insertRecruiter()
        recruitment = recruiter.recruitments[0]

        # Assume
        self.assertEqual(recruiter.name, 'Harold Kumar')
        self.assertEqual(recruiter.mailing_list, None)
        self.assertEqual(recruitment.recruiter_name, recruiter.name)
        endpoint = '/admin/recruiter/update/'
        form_data = dict(
            csrf_token='mock',
            recruiter_id=recruiter.public_id,
            recruiter_name='Updated Recruiter Name',
            recruiter_email=recruiter.email,
            mailing_list='online'
        )
        expected_redirect = '/admin/recruiter/%s/' % (recruiter.public_id)

        # Act
        response = client.post(endpoint, data=form_data, follow_redirects=False)
        recruiter = Recruiter.read(recruiter.public_id)
        recruitment = recruiter.recruitments[0]

        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertEqual(redirect_path(response), expected_redirect)
        self.assertEqual(recruiter.name, form_data['recruiter_name'])
        self.assertEqual(recruiter.mailing_list, form_data['mailing_list'])
        self.assertEqual(recruitment.recruiter_name, form_data['recruiter_name'])

    def test_expects_validation_error_when_update_request_lack_recruiter_email(self):
        # Arrange
        client = recruiters_controller.test_client()
        recruiter = self.insertRecruiter()

        # Assume
        endpoint = '/admin/recruiter/update/'
        form_data = dict(
            csrf_token='mock',
            recruiter_id=recruiter.public_id,
            recruiter_name='Updated Recruiter Name',
            recruiter_email=''
        )
        content_selector = 'div.recruiter.edit'
        form_error_selector = 'form#recruiter-edit div.form-group p.help-block'
        expected_error_message = 'This field is required.'

        # Act
        response = client.post(endpoint, data=form_data, follow_redirects=False)
        html = parse_html(response.data)
        content = html.select_one(content_selector) if html else None
        form_error = content.select_one(form_error_selector) if content else None
        recruiter = Recruiter.read(recruiter.public_id)
        recruitment = recruiter.recruitments[0]

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(content)
        self.assertIsNotNone(form_error)
        self.assertEqual(form_error.text.strip(), expected_error_message)
        self.assertNotEqual(recruiter.name, form_data['recruiter_name'])
        self.assertNotEqual(recruitment.recruiter_name, form_data['recruiter_name'])
