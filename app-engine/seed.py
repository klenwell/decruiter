"""
# Seed File

At present, seed allows you to load recruiter emails from fixtures in using test helper.


## Configuration

This script requires the `google-api-python-client` library to be installed locally:

    pip install google-api-python-client

## Usage

To seed datastore:

    python seed.py -h
    python seed.py
    python seed.py --port=3001

"""
# Python Imports
import sys, os
from os.path import join
import argparse
from datetime import datetime
from pprint import pformat

import config

# Add the Python SDK to the package path.
# See http://stackoverflow.com/a/32926576/1093087
sys.path.append(config.APP_ENGINE_SDK_PATH)
sys.path.append(join(config.APP_ENGINE_SDK_PATH, 'lib/yaml/lib'))
sys.path.append(join(config.APP_ENGINE_SDK_PATH, 'lib/fancy_urllib'))

# Load vendor libs. Taken from appengine_config.py.
from google.appengine.ext import vendor
vendor.add('lib')

# Load App Engine Remote API. Requires google-api-python-client package.
from google.appengine.ext.remote_api import remote_api_stub

from tests.helper import TestEmail
from models.recruiter_email import RecruiterEmail



def main(args):
    args = parse_args(args)
    load_local_api(args.port)
    seed_recruitments()
    return 0

def load_local_api(port):
    host = 'localhost:%s' % (port)
    remote_api_stub.ConfigureRemoteApiForOAuth(host, config.REMOTE_API_PATH, secure=False)


def seed_recruitments():
    fixture_ids = ['20160831_mkhurpe_fwd']
    recruitments = []

    for fixture_id in fixture_ids:
        inbound_message = TestEmail.fixture(fixture_id)
        recruitment = RecruiterEmail.from_inbound_handler(inbound_message)
        recruitments.append(recruitment)

    print 'Seeded %d recruitment(s).' % (len(recruitments))

def parse_args(args):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description="Seed decruiter datastore.")
    parser.add_argument("-p", "--port",
                        type=int,
                        default=config.DEV_API_SERVER_PORT,
                        help="set port number for dev API server")
    return parser.parse_args()

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
