"""
# Recruiters Controller
"""
import logging

from controllers import (app, request, render_template, render_404, redirect, flash,
                         jsonify)
from models.recruiter import Recruiter
from forms.recruiter import RecruiterForm


@app.route('/admin/recruiters/', methods=['GET'])
def recruiters_index():
    page_number = request.args.get('page', 1)
    pager = Recruiter.s_paginated(page_number=page_number)
    recruiters, _, _ = pager.paginate(page_size=25)
    return render_template('recruiters/index.html', recruiters=recruiters, pager=pager)

@app.route('/admin/recruiter/<recruiter_id>/', methods=['GET'])
def recruiter_show(recruiter_id):
    recruiter = Recruiter.read(recruiter_id)

    if not recruiter:
        return render_404('Recruiter not found.')

    return render_template('recruiters/show.html', recruiter=recruiter)

@app.route('/admin/recruiter/<recruiter_id>/edit/', methods=['GET'])
def recruiter_edit(recruiter_id):
    recruiter = Recruiter.read(recruiter_id)

    if not recruiter:
        return render_404('Recruiter not found.')

    form = RecruiterForm()
    form.recruiter_id.data = recruiter.public_id
    form.recruiter_name.data = recruiter.name
    form.recruiter_email.data = recruiter.email

    return render_template('recruiters/edit.html',
                           recruiter=recruiter,
                           form=form)

@app.route('/admin/recruiter/update/', methods=['POST'])
def recruiter_update():
    form = RecruiterForm(request.form)
    recruiter = Recruiter.read(form.recruiter_id.data)

    if not recruiter:
        return render_404('Recruiter not found.')

    if not form.validate_on_submit():
        return render_template('recruiters/edit.html',
                               recruiter=recruiter,
                               form=form)
    else:
        recruiter.update(name=form.recruiter_name.data,
                         email=form.recruiter_email.data,
                         mailing_list=request.form.get('mailing_list'))
        flash('Recruiter successfully update.', 'success')
        return redirect('/admin/recruiter/%s/' % (recruiter.public_id))

@app.route('/admin/recruiter/mailing-list/', methods=['POST'])
def recruiter_mailing_list():
    recruiter_id = request.form.get('recruiter_id')
    mailing_list = request.form.get('mailing_list')
    recruiter = Recruiter.read(recruiter_id)

    if not recruiter:
        return render_404('Recruiter not found.')

    if mailing_list not in recruiter.mailing_lists:
        return jsonify({'error': 'invalid mailing list: %s' % (mailing_list)})
    else:
        recruiter.mailing_list = mailing_list
        recruiter.put()

    response = {
        'recruiter': recruiter.public_id,
        'mailing_list': recruiter.mailing_list
    }
    return jsonify(response)
