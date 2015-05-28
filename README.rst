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

Use the local setting to customize your MI settings
+++++++++++++++++++++++++

    In the masterinterface folder there the .local_settings.py
    It is a good practies to use the local setting in case you have a local instance of the master interface.
    So rename it removing the . (dot) all the parameters defined in the local_setting will override the orginal in the settings.py
    In the default local_setting you can find the default parameters for the development endpoints of the metadata reposiory and the cloud api.
    Remeber to read the comments above each parameters in settings.py before you override them.

Create a new application
+++++++++++++++++++++++++

    To create the application for the master interface just run the command ::

        python manage.py startapp <your_app_name>

    Then update the INSTALLED_APPS in your settings.

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

--------------------------------
Run Celery
--------------------------------

    To support the execution of the workflow the master interface need even to run Celery.
    To start Celery run the command::

        python manage.py celery worker -A masterinterface

    By default celery have 8 workers it means that can run 8 taverna workflow at the same time and use the database backend.
    It is possible to configure the celery cluster in a different wat (rabbitmq / redis  etc..) see the documentation for more information http://docs.celeryproject.org/en/latest/index.html.
    To run it as daemon user supervisor and use the content of the -supervisor_celery_prog.conf- file in the masterinterface folder, copy it in the /etc/supervisor.conf.

--------------------------------
Paraview Web Install guide
--------------------------------
    Paraviewweb is not require to run the masterinterface but you need it if you want to render vtk files via Web.
    The guide to install Paraviewweb is pretty difficult and it need so much patience and some adaptations depending on you operating system.
    Remeber that you have to install the exact version reported in this documentation.

    Paraview in server without GPU need to emulate it using the osmesa library. So first of all you have to install it:
    Omesa 7.9.2 : ftp://ftp.freedesktop.org/pub/mesa/older-versions/7.x/7.9.2/MesaLib-7.9.2.zip
    Paraview 4.0.1: http://www.paraview.org/paraview-downloads/download.php?submit=Download&version=v4.0&type=source&os=all&downloadFile=ParaView-v4.0.1-source.zip
    Requirements::
        cmake >= 2.8.8
        python >= 2.7
        libreria OMesa = 7.9.x
        paraview=4.0.1 64bit

    Unzip opemsa paket and go insde it and run the command::

         ./configure --with-driver=osmesa --prefix=<omesa_installation_folder>
         make
         make install

    If something goes wrong check the system library that you need to install using -apt-get install-.

    Unzip the Paraview source code and remeberd the <paraview-source-code-path> then  outside the soruce folder create a new folder called paraview-build.
    Go inside the paraview-build folder then run this command::

        cmake <paraview-source-code-path> -DPARAVIEW_ENABLE_PYTHON:BOOL=ON -DPARAVIEW_BUILD_QT_GUI:BOOL=OFF -DOPENGL_INCLUDE_DIR:STRING=<omesa_installation_folder>/include  -DOPENGL_glu_LIBRARY:STRING=/usr/mesa/lib/libGLU.so -DVTK_OPENGL_HAS_OSMESA:BOOL=ON -DOSMESA_INCLUDE_DIR:STRING=<omesa_installation_folder>/include -DOSMESA_LIBRARY:STRING=<omesa_installation_folder>/lib/libOSMesa.so -DVTK_USE_X:BOOL=OFF -DOPENGL_gl_LIBRARY:STRING=''

    Replace what is needed in the command according with your installation then ready to build it:

        make
        make install

    By default the paraview will be installed here /usr/local/lib/paraview-4.0/
    Remember to change in the master interface settings the param PARAVIEW_PYTHON_BIN in case you have a different location.


------------------------------------------------
Use the master interface under apache web server
------------------------------------------------

    Some of the features of the master itnerface are developed to work with apache web server (see the institutional folder)
    In the masterinterface folder you can find the -sample-mi_vhost.com- redefine in according with your configuration the follow parameters:

        <port-443-or-80> : define it as port 80 (HTTP) in case you have an SSL certificate user 443 (HTTPS)
        <master-interface-domain> : your master itnerface domain name.
        <master-interface-folder> : your masterinterface folder.
        <authentication-services-folder>: the authtentication folder in this packet.

    After that you can copy it in your apache site-enable folder.
    Remeber to run the command ::

        python manage.py collectstatic

    This permit to apache to serve the static files directly (faster configuration).






