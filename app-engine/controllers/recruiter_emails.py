"""
# Recruiter Emails Controller
"""
import logging

from controllers import (app, render_template)

from models.recruiter_email import RecruiterEmail


@app.route('/admin/recruitments/', methods=['GET'])
def recruitments_index():
    recruitments = RecruiterEmail.s_recently_received(limit=25)
    return render_template('recruiter_emails/index.html', recruitments=recruitments)
