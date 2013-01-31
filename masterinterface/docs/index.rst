.. Vph-Share Master Interface documentation master file, created by
   sphinx-quickstart on Wed Feb 22 11:07:45 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Vph-Share Master Interface's documentation!
======================================================

Contents:

.. toctree::
   :maxdepth: 3


SCS - Masterinterface
================
SCS provide all frontend views to navigate into masterinterface. It Implement Layout-templates and control-views.

Views
--------------
.. autofunction:: masterinterface.scs.views.home
.. autofunction:: masterinterface.scs.views.login
.. autofunction:: masterinterface.scs.views.profile
.. autofunction:: masterinterface.scs.views.login_error
.. autofunction:: masterinterface.scs.views.services
.. autofunction:: masterinterface.scs.views.contacts
.. autofunction:: masterinterface.scs.views.help
.. autofunction:: masterinterface.scs.views.workflows

SCS-Auth
================

Views
--------------
.. automodule:: scs_auth.views

    .. autofunction::  scs_auth.views.done
    .. autofunction::  scs_auth.views.bt_loginform
    .. autofunction::  scs_auth.views.bt_login
    .. autofunction::  scs_auth.views.auth_loginform
    .. autofunction::  scs_auth.views.auth_login
    .. autofunction::  scs_auth.views.auth_done
    .. autofunction::  scs_auth.views.logout
    .. autoclass::  scs_auth.views.validate_tkt
    .. automethod:: scs_auth.views.validate_tkt.read

Models
--------------

.. automodule:: scs_auth.models

Mod_auth_tkt Library
--------------
This library implement methods to create and validate ticket.

.. autofunction::  scs_auth.tktauth.createTicket
.. autofunction::  scs_auth.tktauth.validateTicket

Middleware
--------------
Middleware keep alive session or expire it after 12h.
To do that , when user load any page, the middleware check timestamp into the ticket and validate it ,
if not expire , generates a new ticket with a new timestamp. The ticket is saved into cookie web-browser.

.. autoclass:: scs_auth.preprocess_middleware.masterInterfaceMiddleware

    .. automethod:: scs_auth.preprocess_middleware.masterInterfaceMiddleware.process_view
    .. automethod:: scs_auth.preprocess_middleware.masterInterfaceMiddleware.process_response


Backend
--------------
This section contains all backend into Masterinterface.

Authentication backend - OpenId
++++++++++++++

This section contains authentication backends that implement login controller for openId.

.. autoclass:: scs_auth.backends.biomedtown.BiomedTownBackend

    .. automethod:: scs_auth.backends.biomedtown.BiomedTownBackend.authenticate
    .. automethod:: scs_auth.backends.biomedtown.BiomedTownBackend.get_user_details

.. autoclass:: scs_auth.backends.biomedtown.BiomedTownAuth

    .. automethod:: scs_auth.backends.biomedtown.BiomedTownAuth.openid_url
    .. automethod:: scs_auth.backends.biomedtown.BiomedTownAuth.auth_complete
    .. automethod:: scs_auth.backends.biomedtown.BiomedTownAuth.setup_request

Authentication backend - Mod_auth_tkt
++++++++++++++

This section contains authentication backends that implement login controller for Mod_auth_tkt.

.. autoclass:: scs_auth.backends.biomedtown.BiomedTownTicketBackend

    .. automethod:: scs_auth.backends.biomedtown.BiomedTownTicketBackend.userTicket
    .. automethod:: scs_auth.backends.biomedtown.BiomedTownTicketBackend.authenticate
    .. automethod:: scs_auth.backends.biomedtown.BiomedTownTicketBackend.configure_user

Authentication backend - FromTicket
++++++++++++++

This section contains authentication backends that implement login controller from Ticket (from GET variable).

.. autoclass:: scs_auth.backends.biomedtown.FromTicketBackend

    .. automethod:: scs_auth.backends.biomedtown.FromTicketBackend.authenticate


Auth Extension
--------------
Extension Library for scs_auth.

.. autofunction:: scs_auth.auth.authenticate
.. autofunction:: scs_auth.auth.userProfileUpdate
.. autofunction:: scs_auth.auth.socialtktGen


Cyfronet
================
Cyfronet application provide a basic integration of cyfronet services into masterinterface. It works over iframe.

Views
--------------
.. autofunction:: cyfronet.views.index
.. autofunction:: cyfronet.views.cloudmanager
.. autofunction:: cyfronet.views.datamanager

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
