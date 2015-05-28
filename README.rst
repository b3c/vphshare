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
    project location even the *authentication* regards the authentication services


Python installation requirements
++++++++++++++++++++++++++++++++

    Download and install **Python** from the Python web site: http://www.python.org/download/releases/

    Python version from 2.5 to 2.7 are supported.

    Download and install **setuptools** according to your Python version from http://pypi.python.org/pypi/setuptools

    Download and install **pip** according to your Python version from https://pypi.python.org/pypi/pip

    Move into *vphshare/masterinterface* directory, then run the command::

        pip -f requirements.txt

    All Python dependencies packages will be installed into your system except the mod_auth_tkt library.

    To install the mod_auth_tkt you have to download it manually from https://github.com/b3c/mod_auth/zipball/master

    Unzip the file and move inside the packet then run::

        pytho setup.py install

    **depending on your os, the installation commands may need to be executed as a super user**

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
        #!!!When the system ask you to create the superuser reply NO.
        python manage.py migrate
	

    You will be asked for some information.
    
    Not create Admin user druing the syndb (see 'Create Superuser')

Create Superuser
+++++++++++++++++++++++

    To create a super user you have to apply the migration command before.
    Then
    Run the command ::
        
        python manage.py createsuperuser

    and follow the wizard.
    Remeber you can use the admin user only in the admin backend http://<yourdomain>/admin
    It doesn't work with the login backend of the master interface that work with Biomedtown.


Start and Stop the web application
++++++++++++++++++++++++++++++++++

    From the */vphshare/masterinterface/* directory, simply run the command ::

        python manage.py runserver 8080

    The web application will be reachable at http://locahost:8080

    To stop the service, simply kill the process.

--------------------------------
Create a new application
--------------------------------

    To create the application for the master interface just run the command ::

        python manage.py startapp <your_app_name>

    The master interface use a versioning control of the database called South
    It is important to respect the versioning of your ORM in the models.py
    so each time you create a new model class you have to run the command::

        python manage.py  schemamigration --initial

    Each time you modify your models class you have to run::

        python manage.py  schemamigration --auto

    After that you ahve to apply fisically your model in your database running the command::

        python manage.py migrate

    That's all.
    See the documentation of django south for more info https://south.readthedocs.org/en/latest/





