from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

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
    return render_template('student.html')


# @app.route("/about", methods=['POST'])
# def about():
#     return render_template('www.intellipaat.com')

@app.route("/fetchdata", methods=['GET', 'POST'])
def fetch_student_data():
    # Define the SQL query to fetch data from the "assignment" table
    sql_query = """
        SELECT 
            cohort, intern_period, status, remark, 
            student_name, student_id, student_NRIC, 
            student_gender, student_email, mobile_number, 
            supervior_name, supervisor_email, 
            company_name, company_address, monthly_allowance, 
            company_supervisor_name, company_supervisor_email
        FROM assignment
        WHERE student_id = 123456
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
            "student_email": student_data[8],
            "mobile_number": student_data[9],
            "supervior_name": student_data[10],
            "supervisor_email": student_data[11],
            "company_name": student_data[12],
            "company_address": student_data[13],
            "monthly_allowance": student_data[14],
            "company_supervisor_name": student_data[15],
            "company_supervisor_email": student_data[16]
        }
        return render_template('student.html', student_data=student_dict)
    else:
        return "Student not found"


@app.route("/addcompany", methods=['POST'])
def AddCompany():
    company_name = request.form['companyName']
    company_address = request.form['companyAddress']
    monthly_allowance = request.form['allowance']
    company_supervisor_name = request.form['companySupervisor']
    company_supervisor_email = request.form['companySupervisorEmail']
    company_acceptance_form = request.files['attchCompanyAcceptance']
    parent_acknowledge_form = request.files['attchParentAck']
    letter_of_indemnity = request.files['attchLetterOfIndemnity']
    hired_evidence = request.files['attchHiredEvidence']

    insert_sql = "INSERT INTO assignment (company_name, company_address, monthly_allowance, company_supervisor_name, company_supervisor_email) VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if company_acceptance_form.filename == "" and parent_acknowledge_form.filename == "" and letter_of_indemnity.filename == "" and hired_evidence.filename == "" :
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (company_name, company_address, monthly_allowance, company_supervisor_name, company_supervisor_email))
        db_conn.commit()
        # Uplaod image file in S3 #
        company_acceptance_form_in_s3 = "com-acceptance-form" + \
            str(company_name) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(
                Key=company_acceptance_form_in_s3, Body=company_acceptance_form)
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
            str(company_name) + "_image_file"
        s3 = boto3.resource('s3')
        try:
            s3.Bucket(custombucket).put_object(
                Key=parent_acknowledge_form_in_s3, Body=parent_acknowledge_form)
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
            str(company_name) + "_image_file"
        s3 = boto3.resource('s3')
        try:
            s3.Bucket(custombucket).put_object(
                Key=letter_of_indemnity_in_s3, Body=letter_of_indemnity)
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
            str(company_name) + "_image_file"
        s3 = boto3.resource('s3')
        try:
            s3.Bucket(custombucket).put_object(
                Key=hired_evidence_in_s3, Body=hired_evidence)
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
