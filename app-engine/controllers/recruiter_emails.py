"""
# Recruiter Emails Controller
"""
import logging

from controllers import (app, render_template, render_404)

from models.recruiter_email import RecruiterEmail


@app.route('/admin/recruitments/', methods=['GET'])
def recruitments_index():
    recruitments = RecruiterEmail.s_recently_received(limit=25)
    return render_template('recruiter_emails/index.html', recruitments=recruitments)

@app.route('/admin/recruitment/<public_id>/', methods=['GET'])
def recruitment_show(public_id):
    recruitment = RecruiterEmail.read(public_id)

    if not recruitment:
        return render_404('Recruiter email not found.')

    return render_template('recruiter_emails/show.html', recruitment=recruitment)
