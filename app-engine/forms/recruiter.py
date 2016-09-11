"""
# Recruiter Forms
"""
from flask_wtf import Form
from wtforms import (HiddenField, StringField)
from wtforms.validators import Required, Email

#
# Forms
#
class RecruiterForm(Form):
    recruiter_id            = HiddenField('Prediction Public ID', [Required()])
    recruiter_name          = StringField('Recruiter Name', [Required()])
    recruiter_email         = StringField('Recruiter Email', [Required(), Email()])
