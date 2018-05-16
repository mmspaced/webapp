import pprint
from time import sleep
from threading import Thread

from DB_context_mgr import UseDatabase, DBConnectionError, SQLError
from flask import Flask, render_template, request, redirect, escape, session, copy_current_request_context
from vsearchmodule import search_for_chars
from checker import check_logged_in

# import psycopg2

# It's never a good idea to declare and use a global variable in a web app
# that's using a stateless protocol (HTTP) and supporting multiple users.
# Store the data in session, using Flask's session mechanism.
# record_num = 0

app = Flask (__name__)

# Instead of making the database configuration dictionary global, add it to
# Python's configuration dictionary, app.config

app.config['logdbconfig'] = {'host': '127.0.0.1',
            'user': 'hfwebappuser',
            'password': 'vgirc090',
            'database': 'vsearchlogdb', }

# Add a secret key to Python's configuration dictionary to enable access to
# session data.

app.secret_key = 'YouWillNeverGuess'



# @app.route('/')
# def hello() -> '302':
    # return redirect('/entry')

@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    return render_template('entry.html',
        the_title='Welcome to search_for_chars on the Web!')

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

@app.route('/search4', methods=['POST'])
def do_search() -> str:

    # In order to use copy_current_request_context decorator, the function
    # being decorated (log_request) has to be defined within the function
    # that calls it.  Therefore, we had to move as an inner function

    @copy_current_request_context
    def log_request(req: 'flask_request', res: str) -> None:

        # conn = psycopg2.connect(**logdbconfig)
        # cursor = conn.cursor()

        # Introduce a 15 second delay to test threading.
        # sleep(15)

        try:

            with UseDatabase(app.config['logdbconfig']) as cursor:

                _SQL = """INSERT INTO log 
                            (phrase, letters, ip, browser_string, results) 
                             VALUES(%s, %s, %s, %s, %s)"""

                cursor.execute(_SQL, (req.form['phrase'],
                                      req.form['chars'],
                                      req.remote_addr,
                                      req.user_agent.browser,
                                      results))

        except DBConnectionError as err:
            print('Logging failed with a database connection error: ', str(err))
        except SQLError as err:
            print('Logging failed with SQL syntax error: ', str(err))
        except Exception as err:
            print('Logging failed with the following error: ', str(err))

        # conn.commit()
        # cursor.close()
        # conn.close()

        # global record_num

        # As mentioned above, don't use global variables in a web app.
        # record_num += 1

        # with open('vsearch.log', 'a') as log:
        # print(record_num, req.form, req.remote_addr, req.user_agent, res, file=log, sep=' | ')

    phrase = request.form['phrase']
    chars = request.form['chars']
    results = str(search_for_chars(phrase, chars))
    try:
        # Execute log_request to the database on a separate thread
        t = Thread(target=log_request, args=(request, results))
        t.start()

        # log_request gets called in a separate thread, so comment out here
        # log_request(request, results)

    # Catching these exceptions no longer makes sense because do_search will
    # complete before the log_request thread completes.

    # except DBConnectionError as err:
        # print('Logging failed with a database connection error: ', str(err))
    # except SQLError as err:
        # print('Logging failed with SQL syntax error: ', str(err))

    except Exception as err:
        print('Thread initiation failed with the following error: ', str(err))
        return 'Error'

    return render_template('results.html', the_title='Here are your results...', the_phrase = phrase, the_chars = chars, the_results = results)

@app.route('/viewlog')
@check_logged_in
def view_log() -> str:
    with open('vsearch.log') as log:
        contents = log.readlines()
    return escape(''.join(contents))
#        contents = log.read()
#    return escape(contents)

@app.route('/newviewlog')
@check_logged_in
def new_view_log() -> str:
    with open('vsearch.log') as log:
        list_of_log_record_lists = []
        log_record_list = []
        for log_record in log:
            record_element_list = log_record.split('|')
            for record_element_item in record_element_list:
                log_record_list.append(record_element_item)
        list_of_log_record_lists.append(log_record_list)
        print('list_of_log_record_lists = ', list_of_log_record_lists)
        contents = list_of_log_record_lists
        pprint.pprint(contents)
    return escape(contents)

@app.route('/hfviewlogdb')
@check_logged_in
def hf_view_log_db() -> 'html':
    # contents ends up becoming a list of lists
    contents = []

    # Simulate a 15 second delay in retrieving data from the PostgreSQL database
    # sleep(15)

    # Force a runtime error
    # raise

    try:

        with UseDatabase(app.config['logdbconfig']) as cursor:

            _SQL = """SELECT id, ts, phrase, letters, ip, browser_string, results 
                  from log"""
            cursor.execute(_SQL)

            """for id, ts, phrase, letters, ip, browser_string, results in cursor.fetchall():
                line_element_list = [id, ts, phrase, letters, ip, browser_string, results]
                contents.append(line_element_list)"""

            # I didn't even need the code above, because Python's DB-API fetchall
            # method returns a list of tuples, which is what render_template wants.
            contents = cursor.fetchall()

    except DBConnectionError as err:
        print('Database connection error: ', str(err))
        return 'Error'
    except SQLError as err:
        print('SQL error:', str(err))
        return 'Error'
    except Exception as err:
        print('Something went wrong: ', str(err))
        return 'Error'

    titles = ('Request Number', 'Timestamp', 'Phrase','Letters',
              'Remote Address', 'User Agent', 'Results')
    return render_template('viewlog.html',
                           the_title='View Log',
                           the_row_titles=titles,
                           the_data=contents,)

@app.route('/hfviewlog')
@check_logged_in
def hf_view_log() -> 'html':
    # contents ends up becoming a list of lists
    contents = []
    with open('vsearch.log') as log:
        for line in log:
            line_element_list = []
            # Break each line in the log into a list of elements, based on |
            for item in line.split('|'):
                line_element_list.append(escape(item))
            contents.append(line_element_list)
    titles = ('Request Number', 'Form Data', 'Remote Address', 'User Agent', 'Results')
    return render_template('viewlog.html',
                           the_title='View Log',
                           the_row_titles=titles,
                           the_data=contents,)

# Execute app.run only if vsearch4web is executed directly by Python
# This accommodates running at AWS using PythonAnywhere
if __name__ == '__main__' :
    app.run(debug=True)
