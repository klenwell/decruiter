"""
# Recruiter Emails Controller
"""
import logging

from controllers import (app, render_template, render_404, request, redirect,
                         flash)

from models.recruiter_email import RecruiterEmail
from models.recruiter import Recruiter


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

@app.route('/admin/recruitment/delete/', methods=['POST'])
def recruitment_delete():
    recruitment_id = request.form.get('recruitment_id')
    recruitment = RecruiterEmail.read(recruitment_id)

    if not recruitment:
        return render_404('Recruiter email not found.')

    # Recruitment not necessarily associated with a recruiter.
    recruiter_name = recruitment.recruiter_name or recruitment.recruiter_email
    recruitment.delete()

    flash('Recruitment by %s deleted.' % (recruiter_name), 'success')
    return redirect('/admin/recruitments/')

@app.route('/admin/recruitment/reparse/', methods=['POST'])
def recruitment_reparse():
    recruitment_id = request.form.get('recruitment_id')
    recruitment = RecruiterEmail.read(recruitment_id)

    if not recruitment:
        return render_404('Recruiter email not found.')

    recruitment.extract_recruitment_properties()
    recruiter = Recruiter.get_or_insert_by_recruitment(recruitment)
    recruitment.associate_recruiter(recruiter)

    return redirect('/admin/recruitment/%s/' % (recruitment.public_id))
