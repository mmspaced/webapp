from flask import Flask, session

from checker import check_logged_in

import pprint

app = Flask(__name__)

app.secret_key = 'YouWillNeverGuess'

@app.route('/')
def hello() -> str:
    return 'Hello from the simple webapp.'

@app.route('/page1')
@check_logged_in
def page1() -> str:
    return 'This is page 1.'

@app.route('/page2')
@check_logged_in
def page2() -> str:
    return 'This is page 2.'

@app.route('/page3')
@check_logged_in
def page3() -> str:
    return 'This is page 3.'

@app.route('/login')
def do_login() -> str:
    session['logged_in'] = True
    return 'You are now logged in.'

# Logout functionality seems to work for Chrome but not Safari
@app.route('/logout')
def do_logout() -> str:
    if 'logged_in' in session:
        session.pop('logged_in')
        return 'You are now logged out.'
    return 'You were NOT logged in!'

# Important: It is not possible to check a dictionary for a key's value until
# a key/value pairing exists.  Trying to do so results in a KeyError. To avoid
# the possibility of this error, check for the existence of the key, as
# opposed to to checking the key's actual value.

@app.route('/status')
def check_status() -> str:
    if 'logged_in' in session:
        return 'You are currently logged in.'
    return 'You are NOT logged in.'

# Execute app.run only if vsearch4web is executed directly by Python
# This accommodates running at AWS using PythonAnywhere
if __name__ == '__main__' :
    app.run(debug=True)