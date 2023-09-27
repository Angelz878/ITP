from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from pymysql import connections
from pymysql.cursors import DictCursor
from config import *
import re
  
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

bucket = custombucket
region = customregion

# database connection
# server
db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb
)
output = {}
table = 'assignment'

# home page
@app.route("/", methods=['GET', 'POST'])
def home():
    # check if the users exist or not
    if not session.get("email"):
        # if not there in the session then redirect to the login page
        return redirect("/login")
    
    # Get the student's name from the session
    name = session.get("name")

    return render_template('index.html', name=name)

# login page
@app.route('/login', methods =['GET', 'POST'])
def login():
    # delcare empty message variable
    message = ''

    # if form is submited
    if request.method == 'POST':
        # retrieve email and ic_number from the form data
        email = request.form.get("email")
        ic_number = request.form.get("ic_number")

        # fetch query result as dictionaries
        cursor = db_conn.cursor(DictCursor)
        # query
        cursor.execute('SELECT student_name, student_email, student_NRIC FROM assignment WHERE student_email = % s AND student_NRIC = % s', (email, ic_number))
        login_data = cursor.fetchone()

        # checks if a user with the provided email and password was found in the database.
        if login_data:
            # user found in database
            session['loggedin'] = True
            session['email'] = login_data['student_email']
            session['ic_number'] = login_data['student_NRIC']
            name = login_data['student_name']
            message = 'Logged in successfully !'
            return render_template('index.html', message = message)
        else:
            message = 'Please enter correct email / ic number!'
    return render_template('login.html', message = message)
  
@app.route('/logout')
def logout():
    session["email"] = None
    session['loggedin'] = False
    return redirect(url_for('login'))
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)