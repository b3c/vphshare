vphshare-masterinterface
========================

Welcome to the Vph-Share Master Interface Django project.

------------
Installation
------------

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


Python installation requirements
++++++++++++++++++++++++++++++++

    Download and install **Python** from the Python web site: http://www.python.org/download/releases/

    Python version from 2.5 to 2.7 are supported.

    Download and install **setuptools** according to your Python version from http://pypi.python.org/pypi/setuptools

    Move into *vphshare/masterinterface* directory, then run the command::

        python setup.py install

    **depending on your os, the command may need to be executed as a super user**

    All Python dependencies packages will be installed into your system

------
Django
------

    Django is a powerful and easy to use web framework.

    Django documentation is huge and well written and maintained. Have yourself a look: https://www.djangoproject.com/

    Beside the Django basic (coming soon into this README), all you need to know now is:


Database Syncronization
+++++++++++++++++++++++

    By default, the Master Interface application will store his data into a SQLite datbase.

    The database file will be created at */vphshare/masterinterface/***vphshare.db**

    If you feel the database for certain reason has been corrupted, delete the file and then
    run the command ::

        python manage.py syncdb
        python manage.py migrate
	

    You will be asked for some information.
    
    Not create Admin user in this step please. (see 'Create Superuser')

Database Migration
+++++++++++++++++++++++
    
    When there is a new version of Database schema, Master Interface need to be update schema 
    and data to new version.
    Run the command ::
        
        python manage.py migrate
    
Create Superuser
+++++++++++++++++++++++

    To create a super user you have to apply the migration command before.
    Then
    Run the command ::
        
        python manage.py createsuperuser

    and follow the wizard. 



Start and Stop the web application
++++++++++++++++++++++++++++++++++

    From the */vphshare/masterinterface/* directory, simply run the command ::

        python manage.py runserver 8080

    The web application will be reachable at http://locahost:8080

    To stop the service, simply kill the process.

--------------------------------
Create a new service application
--------------------------------

    To create the interface application for your service within the master interface project,
    just run the command ::

        python wsdl2mi.py <your wsdl url>

    To have an example of what it will be created, try to run the following ::

        python wsdl2mi.py http://www.webservicex.net/sendsmsworld.asmx?WSDL


wsdl2mi limitations at version 0.1
++++++++++++++++++++++++++++++++++

    Only SOAP services

    One service per WSDL

    One port per service

    Complex types can only be a composition of simple types



vphshare-workflowmanager
========================

The workflow manager application is located into the wfmng directory.


------------
Installation
------------

Python installation requirements
++++++++++++++++++++++++++++++++

    First of all you need to have python installed, please refer to the previous section.
    Using pip or easy_install install all packages into requirements.txt (with pip use the command "pip -r requirements.txt")

Local configuration
+++++++++++++++++++

    The wfmng will use a cfg file for the configuration.
    The *wfmng.cfg* file is intended to be used into a production environment, don't modify this file unless you are The President.
    To customize your local configuration create a file *local.wfmng.cfg* in the same directory, the wfmng will use that.
    The *local.wfmng.cfg* is ignored by git, it means you don't have to commit your local configuration ;-)

Database Syncronization
+++++++++++++++++++++++

    Open a msdos/unix shell and go into the wfmng directory and open a python shell.

    Run the following ::

        >> from wfmng import db
        >> db.drop_all() # optional, use it if you want to erase a previous database
        >> db.create_all()
        >> db.session.commit()

Start and Stop the wfmng app
++++++++++++++++++++++++++++

    From the */wfmng/* directory, simply run the command ::

        python wfmng.py -p 5000

    The wfmng app will be reachable at http://locahost:5000

    To stop the service, simply kill the process.