"""
    App Controller Module

    Flask app is loaded here in order to avoid repetition. Controllers should
    import this module.

    Each controller module must have unique function names for their endpoints
    (e.g. journals_index rather than just index). If not, Flask will raise the
    following error:

    AssertionError: View function mapping is overwriting an existing endpoint function
"""
import os
from os.path import dirname, join
from datetime import date, datetime
from functools import wraps
import logging
import urllib

from flask import (Flask, render_template, request, g, flash, redirect, abort,
                   url_for, session, jsonify)
from flask.json import JSONEncoder

from google.appengine.api import users

import config

from flask_wtf.csrf import CsrfProtect


#
# Constants
#
APP_PATH = dirname(dirname(__file__))
TEMPLATE_PATH = join(APP_PATH, 'templates')


#
# Flask App
#
app = Flask(__name__, template_folder=TEMPLATE_PATH)
app.config['ERROR_404_HELP'] = False
app.config['WTF_CSRF_CHECK_DEFAULT'] = False
app.secret_key = config.secrets.FLASK_SECRET_KEY

# Enables CSRF protection. See check_csrf below.
csrf = CsrfProtect(app)


#
# Custom JSON Encode for date objects
# See https://github.com/jeffknupp/sandman/issues/22#issuecomment-35677606
#
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, date):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)
app.json_encoder = CustomJSONEncoder


#
# Template Globals
# http://stackoverflow.com/a/29978965/1093087
#
@app.context_processor
def common_variables():
    return dict(
        current_year = date.today().year,
        deployment_stage = config.DEPLOYMENT_STAGE
    )

#
# Template Helper Methods
#
def at(a_datetime):
    f = '%Y-%m-%d %H:%M:%S'
    if not a_datetime:
        return 'N/A'
    else:
        return a_datetime.strftime(f).lower()

def pager_href(page_number, request):
    args = request.args.copy()
    args['page'] = page_number
    return '?' + urllib.urlencode(args)

@app.context_processor
def template_helpers():
    helpers = dict(
        at = at,
        pager_href = pager_href
    )

    # Make helpers available to jinja
    app.jinja_env.globals.update(**helpers)

    return helpers


## Exception Handlers
@csrf.error_handler
def csrf_error(reason):
    if request.is_xhr:
        return jsonify(error=reason), 400
    else:
        return render_template('400.html', message=reason), 400

@app.errorhandler(403)
def forbidden(e):
    """Return a custom 403 error."""
    message = str(e)
    return render_403(message)

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return render_404()

@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    if request.is_xhr:
        return jsonify(error=e), 500
    else:
        return render_template('500.html', error=e), 500

## Alternate Exception handlers
def render_404(message=None):
    if not message:
        message = 'Page not found.'
    if request.is_xhr:
        return jsonify(error=message), 404
    else:
        return render_template('404.html', message=message), 404

def render_403(message=None):
    if not message:
        message ="Sorry. You can't see this page."

    if request.is_xhr:
        return jsonify(error=message), 403
    else:
        return render_template('403.html', message=message), 403

#
# Request Callbacks
#
@app.before_request
def set_app_engine_user():
    g.app_engine_user = users.get_current_user()
    g.app_engine_admin = users.is_current_user_admin()

@app.before_request
def check_csrf():
    # ACCEPT_MOCK_CSRF_TOKEN config can be set in test config. If set, any
    # submitted CSRF token will satisfy CSRF check.
    if app.config.get('ACCEPT_MOCK_CSRF_TOKEN', False):
        if request.form.get('csrf_token'):
            return

    if request.method in app.config['WTF_CSRF_METHODS']:
        return csrf.protect()

#
# Workflow Filters
#
def redirect_on_cancel():
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if request.form.get('cancel'):
                return redirect(request.form['cancel-redirect'])
            return f(*args, **kwargs)
        return wrapped
    return wrapper
