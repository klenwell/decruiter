# Decruiter

An Python Flask App Engine application for quickly deconstructing and categorizing recruiter emails.

- App Engine Site: TBA
- Trello Board: https://trello.com/b/6exW1pbZ/decruiter


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

    cp -v decruiter/app-engine/config/secrets.py{-dist,}

Update secret values in news `secrets.py`.


## Development Server

To launch the local development server:

    dev_appserver.py --port=3000 --admin_port=3001 --api_port=3002 ./app-engine

Application will run on [http://localhost:3000](http://localhost:3000).


## Tests

No tests yet.


## Deployment

To deploy the App Engine application:

    appcfg.py -A PROJECT_NAME -e YOUR_USER_NAME update ./app-engine
