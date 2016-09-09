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
        mail_message = TestEmail.fixture('20160831_mkhurpe_fwd')
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
        expected_recruiter_name = 'Mahesh Khurpe'

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
        self.assertEqual(content.h2.text.strip(), 'Recruiters')
        self.assertEqual(len(table_rows), 1)
        self.assertEqual(table_rows[0].td.text.strip(), expected_recruiter_name)

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
        expected_recruiter_name = 'Mahesh Khurpe'
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
