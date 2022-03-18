
duma_backend
============

TODO: update this !!!!!

Quick intro of project goes here.

Installation
============

.. code:: bash

    pip install duma_backend


Configuration
=============

The application can configured like any other Flask application.

First it will load the bundled `settings.py` file to configure sensible defaults.
Please see `settings.py` and https://terndatateam.bitbucket.io/flask_tern/ for details.

Next it will look for an environment variable `DUMA_BACKEND_SETTINGS`. This environment variable
should point to a python file which will be loaded as well. The format is exactly the same as in `settings.py` .

This project uses ``flask_tern``. Be sure to check documentation and code https://bitbucket.org/terndatateam/flask_tern .

Flask-Cors: https://flask-cors.readthedocs.io/en/latest/


Development
===========

Clone the source code and cd into the directory of your local copy.
You may want to adapt settings in .flaskenv

.. code:: bash

    # install project in editable mode
    pip install -e '.[testing,docs]'
    # to run tests use
    pytest
    # coverage report
    pytest --cov --cov-report=html


The same can be done within a docker environment. The following is a simple example using alpine.

.. code:: bash

    docker run --rm -it -p 5000:5000 -v "$(pwd)":/duma_backend -w /duma_backend alpine:3.10 sh
    # install python in binary libs in container
    apk add python3 py3-cryptography
    # install pkg in container
    pip3 install -e '.[testing]'
    # run tests inside container
    pytest
    pytest --cov --cov-report=html


Run flask development server.

.. code:: bash

    # locally
    flask run
    # within container
    flask run -h 0.0.0.0

The app can then be accessed at http://localhost:5000


Database management
===================

The project uses Flask-Migrate to manage databes schemas.
Flask-Migrate uses Alembic to manage database migrations. As a first step it is
necessary to initialise the Alembic configuration with `flask db init`. This will create a
module `duma_backend.migrations` with the necessarry settings and boilerplate for Alembic.
Whenever there are changes to the database models, it is necessary to create a new migration step and apply this migration to the database.
Per default the development environment uses sqlite as database backend, but this can easily be change by reconfiguring Flask-SQLAlchemy.

.. code:: bash

    # init migrations
    flask db init

    # the following two steps are necessary when changing database models
    # create new mgration / revision
    flask db migrate

    # update / create db. this step also initialises an empty database with the latest db schema.
    flask db upgrade
