"""
# Recruiters Controller
"""
import logging

from controllers import (app, render_template, render_404)

from models.recruiter import Recruiter


@app.route('/admin/recruiters/', methods=['GET'])
def recruiters_index():
    recruiters = Recruiter.s_recently_created(limit=25)
    return render_template('recruiters/index.html', recruiters=recruiters)

@app.route('/admin/recruiter/<public_id>/', methods=['GET'])
def recruiter_show(public_id):
    recruiter = Recruiter.read(public_id)

    if not recruiter:
        return render_404('Recruiter not found.')

    return render_template('recruiters/show.html', recruiter=recruiter)
