from django.contrib.auth import get_backends
from django.conf import settings


def authenticate(**credentials):
    """
Override orginal authenticate to support ticket retrun.
Now, If the given credentials are valid, return a User object and ticket.
"""
    for backend in get_backends():
        try:
            user = backend.authenticate(**credentials)
        except TypeError:
            # This backend doesn't accept these credentials as arguments. Try the next one.
            continue
        if user is None:
            continue
            # Annotate the user object with the path of the backend.
        if isinstance(user, tuple):
            user[0].backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        else:
            user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        return user
