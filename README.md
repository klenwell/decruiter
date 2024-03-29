# Decruiter

An Python Flask App Engine application for quickly deconstructing and categorizing recruiter emails.

- ~~App Engine Site: https://decruiter.appspot.com/ ~~
- Trello Board: https://trello.com/b/6exW1pbZ/decruiter

**This project has been archived and is no longer active.**


## Flask App Engine Application

The Flask App Engine application is based on the [GoogleCloudPlatform Flask App Engine
skeleton](https://github.com/GoogleCloudPlatform/appengine-python-flask-skeleton).

To install:

1. Install the [Google App Engine Python SDK](https://cloud.google.com/appengine/downloads).

2. Clone this repository:

         git clone https://github.com/klenwell/decruiter.git

3. Install the required libraries using Pip:

         cd decruiter/app-engine
         pip install -r requirements.txt -t lib

4. Create secrets file by copying `-dist` version into place:

         cp -v app-engine/config/secrets.py{-dist,}

    Update secret values in news `secrets.py`.

5. Update automated reply template.

    If you configure your app to send automated replies, you'll probably want to update the email template found at `templates/emails/recruitment_reply.txt`


## Development Server

To launch the local development server, run the following command from the project root:

    PYENV_VERSION=2.7.13 dev_appserver.py --port=3000 --admin_port=3001 --api_port=3002 ./app-engine

Application will run on [http://localhost:3000](http://localhost:3000).


## Tests

First, install testing libraries:

    cd app-engine
    pip install -r requirements-test.txt

Then update the settings in `nose.cfg`, especially `gae-lib-root`:

    gae-lib-root=/home/klenwell/opt/google_appengine

To run tests:

    cd app-engine
    nosetests -c nose.cfg

With coverage:

    nosetests -c nose.cfg --with-coverage --cover-erase \
      --cover-package=config,models

To run a single test:

    cd app-engine
    nosetests -c nose.cfg tests/models/test_recruiter_email.py


## Deployment

To deploy the App Engine application:

    appcfg.py -A PROJECT_NAME -e YOUR_USER_NAME update ./app-engine
