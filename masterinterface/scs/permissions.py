
from functools import wraps

def checkSamplePermission(f):
    """ Function decorator mock up
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated
