from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from pymysql import connections
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
    return render_template('index.html')

# login page
@app.route('/login', methods =['GET', 'POST'])
def login():
    # delcare empty message variable
    mesage = ''

    # if form is submited
    if request.method == 'POST' and 'email':
        # record the email
        session['email'] = request.form.get("email")
        # redirect to the main page
        email = request.form['email']
        ic_number = request.form['ic_number']
        # fetch query result as dictionaries
        cursor = db_conn.cursor(connections.cursor.DictCursor)
        # query
        cursor.execute('SELECT * FROM assignment WHERE student_email = % s AND student_NRIC = % s', (email, ic_number))
        assignment = cursor.fetchone()
        # checks if a user with the provided email and password was found in the database.
        if assignment:
            session['loggedin'] = True
            session['email'] = assignment['email']
            session['ic_number'] = assignment['ic_number']
            message = 'Logged in successfully !'
            return render_template('user.html', message = message)
        else:
            message = 'Please enter correct email / ic number!'
    return render_template('login.html', message = message)
  
@app.route('/logout')
def logout():
    session["email"] = None
    session['loggedin'] = False
    return redirect(url_for('login'))
    
if __name__ == "__main__":
    app.run()