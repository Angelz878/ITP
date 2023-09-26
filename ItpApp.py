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



@app.route("/addcompany", methods=['POST'])
def AddCompany():
    company_name = request.form['companyName']
    company_address = request.form['companyAddress']
    monthly_allowance = int(request.form['allowance'])  # Convert to int
    company_supervisor_name = request.form['companySupervisor']
    company_supervisor_email = request.form['companySupervisorEmail']
    company_acceptance_form = request.files['attchCompanyAcceptance']
    parent_acknowledge_form = request.files['attchParentAck']
    letter_of_indemnity = request.files['attchLetterOfIndemnity']
    hired_evidence = request.files['attchHiredEvidence']

    insert_sql = "INSERT INTO assignment VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if (company_acceptance_form.filename == "" and parent_acknowledge_form.filename == "" and letter_of_indemnity.filename == "") or hired_evidence.filename == "":
        return "Please select a file"

    try:
        cursor.execute(insert_sql, (company_name, company_address, monthly_allowance, company_supervisor_name, company_supervisor_email))
        db_conn.commit()

        # Upload files to S3 with unique object URLs
        s3 = boto3.resource('s3')

        def upload_to_s3(file, s3_key):
            try:
                s3.Bucket(custombucket).put_object(Key=s3_key, Body=file)
                bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                s3_location = (bucket_location.get('LocationConstraint') or '').lstrip('-')
                return f"https://s3-{s3_location}.amazonaws.com/{custombucket}/{s3_key}"
            except Exception as e:
                return str(e)

        company_acceptance_url = upload_to_s3(company_acceptance_form, f"com-acceptance-form-{company_name}_image_file")
        parent_acknowledge_url = upload_to_s3(parent_acknowledge_form, f"parent-ack-form-{company_name}_image_file")
        letter_of_indemnity_url = upload_to_s3(letter_of_indemnity, f"letter-of-indemnity-form-{company_name}_image_file")
        hired_evidence_url = upload_to_s3(hired_evidence, f"hired-evidence-form-{company_name}_image_file")

    except Exception as e:
        return f"An error occurred: {str(e)}"
    
    finally:
        cursor.close()

    print("All modifications done...")
    return render_template('student.html')
