# Configuration Settings
import os
from datetime import datetime
from config import secrets


# Set deployment stage: production (default), development, or test
if os.environ.get('SERVER_SOFTWARE', '').startswith('Development'):
    DEPLOYMENT_STAGE = 'development'
elif os.environ.get('SERVER_SOFTWARE', '') == 'TEST':
    DEPLOYMENT_STAGE = 'test'
else:
    DEPLOYMENT_STAGE = 'production'

PROJECT_NAME = 'Decruiter'

# Local Dev Server Settings (used by seed.py)
APP_ENGINE_SDK_PATH = '/home/klenwell/opt/google_appengine/'
DEV_API_SERVER_PORT = 9002
REMOTE_API_PATH = '/_ah/remote_api'

# This value can be used for Reddit-like time-sensitive scoring algorithms.
PROJECT_BIRTHDATE = datetime(2016, 1, 1, 0, 0, 0)
