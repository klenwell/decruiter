"""
# Pages Controller Test

To run individually:

    nosetests -c nose.cfg tests/controllers/test_pages.py
"""
from controllers.pages import app as recruiters_controller
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
    def test_expects_index_to_display_recruitment_count(self):
        # Arrange
        client = recruiters_controller.test_client()
        recruiter = self.insertRecruiter()

        # Assume
        self.assertEqual(Recruiter.query().count(), 1)
        self.assertEqual(recruiter.email_count, 1)
        endpoint = '/'
        content_selector = 'div.home'
        stats_selector = 'h4.stats'
        expected_stats = ''

        # Act
        response = client.get(endpoint, follow_redirects=False)
        html = parse_html(response.data)
        content = html.select_one(content_selector) if html else None
        stats = content.select_one(stats_selector) if content else None

        # Assert
        self.assertEqual(response.status_code, 200, html)
        self.assertIsNotNone(content)
        self.assertIsNotNone(stats)
        self.assertEqual(content.h1.text.strip(), 'Decruiter')
        self.assertTrue(stats.text.strip().startswith(expected_stats))
