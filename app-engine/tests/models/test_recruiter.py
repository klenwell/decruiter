"""
# Recruiter Model Tests

To run individually:

    nosetests -c nose.cfg tests/models/test_recruiter.py
"""
from models.recruiter import Recruiter

from tests.helper import AppEngineModelTest


#
# Test Case
#
class RecruiterModelTest(AppEngineModelTest):
    def test_expects_to_create_model_instance(self):
        recruiter = Recruiter()
        self.assertIsInstance(recruiter, Recruiter)
