============
scoring api
============

Introduction
============

api.py - Scoring service HTTP server
kvs.py - Key Value Storage server

.. contents::


Usage
=====

Options

.. code-block:: 

    ./api.py [-p PORT] [-l LOG_FILE_NAME] [-s HOST,PORT,TIMEOUT,TRIES]

        score service server

        -p : port to be listened, default 8080

        -l : log file name, default print to stderr

        -s : store KVS config, default localhost,8010,10,3

    ./kvs.py 

        key value storage server

        -p : port to be listened, default 8080

        -l : log file name, default print to stderr

        -s : path to storage directory, default .

    ./test.py [-v]

        test suite

        -v : verbose flag


Example
-------

Execute score server:

.. code-block:: 

    ./api.py

Execute kvs server:

.. code-block:: 

    ./kvs.py

Execute test suite:

.. code-block:: 

    ./test.py