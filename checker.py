""" Decorator used in simple_webapp to determine if user is logged in before
    displaying particular web pages.  This provides a modular mechanism to
    restrict access to certain URLs in a web application. """

from flask import session

from functools import wraps

def check_logged_in(func: object) -> object:

    @wraps(func)

    def wrapper(*args, **kwargs):
        if 'logged_in' in session:
            return func(*args, **kwargs)
        return 'You are NOT currently logged in.'

    return wrapper

