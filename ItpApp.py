from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from pymysql import connections
import os
import boto3
from config import *
import secrets

app = Flask(__name__)

# Set a secret key for session management
secret_key = secrets.token_hex(24)
app.config['SECRET_KEY'] = secret_key

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'assignment'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route("/redirecthome", methods=['GET', 'POST'])
def RedirectHome():
    return render_template('index.html')

@app.route("/redirectlogin", methods=['GET', 'POST'])
def RedirectLogin():
    return render_template('login.html')

@app.route("/redirectregister", methods=['GET', 'POST'])
def RedirectRegister():
    return render_template('register.html')

@app.route("/redirectstudentpage", methods=['GET', 'POST'])
def RedirectStudentPage():
    return render_template('student.html')



@app.route("/fetchdata", methods=['GET', 'POST'])
def fetch_student_data():
    # Check if the user is logged in (session contains 'loggedin')
    if 'loggedin' in session:
        # Access the student_id from the session
        student_id = session['student_id']
        
        # Define the SQL query to fetch data from the "assignment" table based on the student_id
        sql_query = """
            SELECT 
                cohort, intern_period, status, remark, 
                student_name, student_id, student_NRIC, 
                student_gender, student_programme, student_email, mobile_number, 
                supervisor_name, supervisor_email
            FROM assignment
            WHERE student_id = %s
        """

        cursor = db_conn.cursor()
        cursor.execute(sql_query, (student_id,))
        student_data = cursor.fetchone()

        if student_data:
            # Convert the fetched data into a dictionary
            student_dict = {
                "cohort": student_data[0],
                "intern_period": student_data[1],
                "status": student_data[2],
                "remark": student_data[3],
                "student_name": student_data[4],
                "student_id": student_data[5],
                "student_NRIC": student_data[6],
                "student_gender": student_data[7],
                "student_programme": student_data[8],
                "student_email": student_data[9],
                "mobile_number": student_data[10],
                "supervisor_name": student_data[11],
                "supervisor_email": student_data[12],
            }

            return jsonify(student_dict)
        else:
            return "Student not found"
    else:
        return jsonify({"error": "Not logged in"})

@app.route("/updatesupervisor", methods=['POST'])
def UpdateSupervisor():
    
    student_id = session['student_id']
    supervisor_name = request.form['ucSupervisor']
    supervisor_email = request.form['ucSupervisorEmail']

    update_sql = "UPDATE assignment SET supervisor_name = %s, supervisor_email = %s WHERE student_id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(update_sql, (supervisor_name, supervisor_email, student_id))
        db_conn.commit()
        
    except Exception as e:
        db_conn.rollback()  # Rollback changes if an error occurs
        print(f"Error: {e}")
        
    finally:
        cursor.close()

    return render_template('student.html')


@app.route("/addcompany", methods=['POST'])
def AddCompany():
    student_id = session['student_id']
    
    company_name = request.form['companyName']
    company_address = request.form['companyAddress']
    monthly_allowance = request.form['allowance']
    company_supervisor_name = request.form['companySupervisor']
    company_supervisor_email = request.form['companySupervisorEmail']
    company_acceptance_form = request.files['attchCompanyAcceptance']
    parent_acknowledge_form = request.files['attchParentAck']
    letter_of_indemnity = request.files['attchLetterOfIndemnity']
    hired_evidence = request.files['attchHiredEvidence']

    update_sql = "UPDATE assignment SET company_name = %s, company_address = %s, monthly_allowance = %s, company_supervisor_name = %s, company_supervisor_email = %s, status = 'Applied'"
    cursor = db_conn.cursor()

    if company_acceptance_form.filename == "" and parent_acknowledge_form.filename == "" and letter_of_indemnity.filename == "" and hired_evidence.filename == "":
        return "Please select a file"

    try:

        cursor.execute(update_sql, (company_name, company_address,
                       monthly_allowance, company_supervisor_name, company_supervisor_email))
        db_conn.commit()
        # Uplaod image file in S3 #
        company_acceptance_form_in_s3 = "com-acceptance-form" + \
            str(student_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(
                Key=company_acceptance_form_in_s3, Body=company_acceptance_form, ContentType='application/pdf')
            bucket_location = boto3.client(
                's3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                company_acceptance_form_in_s3)

        except Exception as e:
            return str(e)

        parent_acknowledge_form_in_s3 = "parent-ack-form" + \
            str(student_id) + "_image_file"
        s3 = boto3.resource('s3')
        try:
            s3.Bucket(custombucket).put_object(
                Key=parent_acknowledge_form_in_s3, Body=parent_acknowledge_form, ContentType='application/pdf')
            bucket_location = boto3.client(
                's3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                parent_acknowledge_form_in_s3)

        except Exception as e:
            return str(e)

        letter_of_indemnity_in_s3 = "letter-of-indemnity-form" + \
            str(student_id) + "_image_file"
        s3 = boto3.resource('s3')
        try:
            s3.Bucket(custombucket).put_object(
                Key=letter_of_indemnity_in_s3, Body=letter_of_indemnity, ContentType='application/pdf')
            bucket_location = boto3.client(
                's3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                letter_of_indemnity_in_s3)

        except Exception as e:
            return str(e)

        hired_evidence_in_s3 = "hired-evidence-form" + \
            str(student_id) + "_image_file"
        s3 = boto3.resource('s3')
        try:
            s3.Bucket(custombucket).put_object(
                Key=hired_evidence_in_s3, Body=hired_evidence, ContentType='application/pdf')
            bucket_location = boto3.client(
                's3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                hired_evidence_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("All modification done...")
    # return render_template('student.html', name=emp_name)
    return render_template('student.html')

@app.route("/addcand", methods=['POST'])
def AddCandidate():
    # Extract form data from the registration form
    level = request.form.get('level')
    cohort = request.form.get('cohort')
    student_programme = request.form.get('student_programme')
    intern_period = request.form['intern_period']
    student_group = request.form['student_group']
    student_id = request.form['student_id']
    student_email = request.form['student_email']
    cgpa = request.form['cgpa']
    supervisor_name = request.form['supervisor_name']
    supervisor_email = request.form['supervisor_email']
    student_name = request.form['student_name']
    student_NRIC = request.form['student_NRIC']
    student_gender = request.form.get('student_gender')
    remark = request.form['remark']    
    student_address = request.form['student_address']
    mobile_number = request.form['mobile_number']
    
    # SQL insert statement for inserting all data into a single table
    insert_sql = "INSERT INTO assignment (level, cohort, student_programme, intern_period, student_group, student_id, student_email, cgpa, supervisor_name, supervisor_email, student_name, student_NRIC, student_gender, remark, student_address, mobile_number, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')"

    cursor = db_conn.cursor()

    try:
        # Execute SQL insert statement
        cursor.execute(insert_sql, (level, cohort, student_programme, intern_period, student_group, student_id, student_email, cgpa, supervisor_name, supervisor_email, student_name, student_NRIC, student_gender, remark,student_address, mobile_number))

        db_conn.commit()

    finally:
        cursor.close()

    print("all modifications done...")
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # declare an empty message variable
    message = ''

    # if the form is submitted
    if request.method == 'POST':
        # retrieve email and ic_number from the form data
        email = request.form.get("student_email")
        ic_number = request.form.get("student_NRIC")

        # fetch query result as tuples
        cursor = db_conn.cursor()
        # query
        cursor.execute('SELECT student_name, student_email, student_NRIC, student_id FROM assignment WHERE student_email = %s AND student_NRIC = %s', (email, ic_number))
        login_data = cursor.fetchone()

        # checks if a user with the provided email and password was found in the database.
        if login_data:
            # user found in the database
            session['loggedin'] = True
            session['email'] = login_data[1]  # Access elements by index
            session['ic_number'] = login_data[2]  # Access elements by index
            session['student_id'] = login_data[3]  # Store student ID in the session
            name = login_data[0]  # Access elements by index
            message = 'Logged in successfully!'
            return render_template('student.html', message=message)  # Redirect to the student home page
        else:
            message = 'Please enter correct email / ic number!'
    
    return render_template('student.html', message=message)


  
@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    return render_template('login.html')  # Redirect to the login page after logout

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
