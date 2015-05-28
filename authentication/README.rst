vphshare-authentication services
========================

Welcome to the Vph-Share Master Authentications.
------------
Some story
------------
    This tool born initialli like a tentative to detach the biomedtown portal (based on the plne framework) as identity provider and use only a dedicated api based on a lightweight as FLASK.
    This services are used by the MI only to authenticate the users and redirect them to the taverna online,
    It is used to refresh the ticket only in limitated case used by the developers . It is not perfect and probably have some bugs, unfortunately we didn't have developers/time to work on it any more.
    In conclusion I suggest you to remove it in future and replace it with your identity provider apis. How to do that , it is your choice.
    In any case if you have a question about it means you are following the dark side of the Force, young Skywalker.

------------
Installation
------------

    The authentication services are based on flask so install it using pip.
    Configure dbconnection with your postgres instance.
    Load the schema using the command::

        psql <yourdatabase> < ./biomedtown-auth-schema.sql

    That's all , or at least I hope that's all.