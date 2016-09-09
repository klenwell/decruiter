"""
# Seed File

At present, seed allows you to load recruiter emails from fixtures in using test helper.


## Configuration

This script requires the `google-api-python-client` library to be installed locally:

    pip install google-api-python-client

## Usage

To seed datastore:

    python seed.py

"""
# Python Imports
import sys, os
from os.path import join
from datetime import datetime
from pprint import pformat

# Constants
# TODO: Make SDK path a config setting.
APP_ENGINE_SDK_PATH = '/home/klenwell/google-cloud-sdk/platform/google_appengine/'
LOCAL_API_SERVER_PORT = 9002
REMOTE_API_PATH = '/_ah/remote_api'

# Add the Python SDK to the package path.
# See http://stackoverflow.com/a/32926576/1093087
sys.path.append(APP_ENGINE_SDK_PATH)
sys.path.append(join(APP_ENGINE_SDK_PATH, 'lib/yaml/lib'))
sys.path.append(join(APP_ENGINE_SDK_PATH, 'lib/fancy_urllib'))

# Load vendor libs. Taken from appengine_config.py.
from google.appengine.ext import vendor
vendor.add('lib')

# Load App Engine Remote API. Requires google-api-python-client package.
from google.appengine.ext.remote_api import remote_api_stub

from tests.helper import TestEmail
from models.recruiter_email import RecruiterEmail


def main(args):
    load_local_api()
    seed_recruitments()

# TODO: make API port command line option.
def load_local_api():
    host = 'localhost:%s' % (LOCAL_API_SERVER_PORT)
    remote_api_stub.ConfigureRemoteApiForOAuth(host, REMOTE_API_PATH, secure=False)


def seed_recruitments():
    fixture_ids = ['20160831_mkhurpe_fwd']
    recruitments = []

    for fixture_id in fixture_ids:
        inbound_message = TestEmail.fixture(fixture_id)
        recruitment = RecruiterEmail.from_inbound_handler(inbound_message)
        recruitments.append(recruitment)

    print 'Seeded %d recruitment(s).' % (len(recruitments))



if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
