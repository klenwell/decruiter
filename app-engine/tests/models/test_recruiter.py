"""
# Recruiter Model Tests

To run individually:

    nosetests -c nose.cfg tests/models/test_recruiter.py
"""
from models.recruiter import Recruiter, MAILING_LISTS

from tests.helper import AppEngineModelTest


#
# Test Case
#
class RecruiterModelTest(AppEngineModelTest):
    def test_expects_to_create_model_instance(self):
        recruiter = Recruiter()
        self.assertIsInstance(recruiter, Recruiter)

    def test_expects_to_add_recruiter_to_mailing_list(self):
        # Arrange
        recruiter = Recruiter(email='recruiter@hotmail.com',
                              name='Reed Cruiter')
        recruiter.put()

        # Assume
        self.assertEqual(recruiter.mailing_list, None)

        # Act
        recruiter.mailing_list = MAILING_LISTS[0]
        recruiter.put()

        # Assert
        self.assertEqual(recruiter.mailing_list, MAILING_LISTS[0])

    def test_expects_recruiter_first_name(self):
        # Act
        recruiter = Recruiter(email='recruiter@hotmail.com',
                              name='Robert E. Cruiter')

        # Assert
        self.assertEqual(recruiter.first_name, 'Robert')
