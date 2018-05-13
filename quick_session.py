from flask import Flask, session

app = Flask(__name__)

app.secret_key = 'YouWillNeverGuess'

@app.route('/setuser/<user>')
def setuser(user:str) -> str:
    session['user'] = user
    return 'setuser() user value is currently set to :' + session['user']

@app.route('/getuser')
def getuser() -> str:
    return 'getuser() user value is currently set to: ' + session['user']

# Execute app.run only if vsearch4web is executed directly by Python
# This accommodates running at AWS using PythonAnywhere
if __name__ == '__main__' :
    app.run(debug=True)








