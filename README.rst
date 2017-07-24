.. image:: https://circleci.com/gh/EugeneBad/bucketlist.svg?style=svg
    :target: https://circleci.com/gh/EugeneBad/bucketlist


.. image:: https://codecov.io/gh/EugeneBad/bucketlist/branch/dev/graph/badge.svg
  :target: https://codecov.io/gh/EugeneBad/bucketlist

===========
BUCKETLISTS
===========

A bucketlist is a list of things that one has not done before but wants to do before dying; and this
application provides the ease and convenience of securely creating, viewing and editing bucketlists
and items within them using a Flask API backend.

Usage
#####
To get started with the application, clone it from github into a python environment using:
::

        git clone http://github.com/EugeneBad/bucketlists.git

Navigate into the *bucketlists* directory and install dependencies by running:
::

        pip install -r requirements.txt

Launch the application by running:
::

        python run.py

To run tests, use the command:
::

        APP_SETTINGS=config.Testing pytest tests

