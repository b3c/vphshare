vphshare-masterinterface
========================

Welcome to the Vph-Share Master Interface Django project.


Installation
------------


Python installation requirements
++++++++++++++++++++++++++++++++

    Download and install **Python** from the Python web site: http://www.python.org/download/releases/

    Python version from 2.5 to 2.7 are supported.

    Download and install **setuptools** according to your Python version from http://pypi.python.org/pypi/setuptools

    Move into vphshare/masterinterface directory, then run the command::

        python setup.py install

    **depending on your os, the command may need to be executed as a super user**

    All Python dependencies packages will be installed into your system


Git installation requirements
+++++++++++++++++++++++++++++

    Download and install the git client http://git-scm.com/download

    Register to the github service https://github.com/


Clone our repository with git
+++++++++++++++++++++++++++++

    Move to the local directory you want to deploy the application to then run the command ::

        git clone https://<your username>@github.com/b3c/vphshare.git

    By default, git will clone the repository into the *./vphshare/masterinterface* directory

    While the *vphshare* directory is meant to be just a container, the *masterinterface* directory will be the base
    project location


Django
++++++

    Django is a powerful and easy to use web framework.

    Django documentation is huge and well written and maintained. Have yourself a look: https://www.djangoproject.com/

    Beside the Django basic (coming soon into this README), all you need to know now is:


Database Syncronization
***********************

    By default, the Master Interface application will store his data into a SQLite datbase.

    The database file will be created at */vphshare/masterinterface/***vphshare.db**

    If you feel the database for certain reason has been corrupted, delete the file and then
    run the command ::

        python manage.py syncd

    You will be asked for some information.

    Admin user is not mandatory for our purposes, its creation is at your will.


Start and Stop the web application
**********************************

    From the */vphshare/masterinterface/* directory, simply run the command ::

        python manage.py runserver 8080

    The web application will be reachable at http://locahost:8080

    To stop the service, simply kill the process.


Create a new service application
++++++++++++++++++++++++++++++++

    To create the interface for your service within the master interface application,
    just run the command ::

        python manage.py wsdl2mi.py <your wsdl url>

    To have an example of what it will be created, run the following ::

        python manage.py http://www.webservicex.net/sendsmsworld.asmx?WSDL

    More detailed description is coming soon


wsdl2mi limitations at version 0.1
++++++++++++++++++++++++++++++++++

    One service per WSDL

    Complex types can only be a composition of simple types


