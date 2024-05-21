from apps.home import blueprint
from flask import render_template, request,redirect,url_for
from flask_login import login_required,current_user
from jinja2 import TemplateNotFound
import json
import os
import csv
import smtplib
from email.message import EmailMessage
import sqlite3



current_directory = os.getcwd()

print("Current Directory:", current_directory)
global jsonath2
new=os.path.join(current_directory,'apps')
jsonath=os.path.join(new,'db.sqlite3')

def savemail():
    try:
        with open('email.json','r') as file:
            return(json.load(file))
    except FileNotFoundError:
        return {"emails": {"data": []}}
        
def addemail(data):
    with open('email.json','w') as file:
        json.dump(data, file, indent=2)

emailsdata=savemail()

def mailda():
    cuslist = [doc for doc in emailsdata['emails']['data']]
    
    return cuslist


def inserdata(email,Subject,msg,status):
    conn = sqlite3.connect(jsonath)
    cursor = conn.cursor()
    query = f"INSERT INTO sentstatus (email, subjects, messages, status) VALUES ('{email}', '{Subject}', '{msg}', '{status}')"
    cursor.execute(query)
    conn.commit()
    data = cursor.fetchall()
    
def alldata():
    conn = sqlite3.connect(jsonath)
    cursor = conn.cursor()
    query = f"SELECT * FROM sentstatus"
    cursor.execute(query)
    data = cursor.fetchall()
    return data

@blueprint.route('/index')
@login_required
def index():
    data=alldata()
    download_data=f"static\sampledata\emails.csv"
    return render_template('home/index.html', segment='index', current_user=current_user,download_data=download_data,cuslist=mailda(),data=data)

@blueprint.route("/send_mails")
@login_required
def mailsend():
    senderemail = request.args.get('senderem')
    recieverem = request.args.get('recverem')
    attach = request.args.get('attach')
    subject = request.args.get('subject')
    msg = request.args.get('messages')
    
    print(senderemail, recieverem, attach, subject, msg)
    
    get_email = [doc for doc in emailsdata['emails']['data'] if doc['email'] == str(senderemail)]
    if not get_email:
        return "Sender email not found", 400
    
    def send_email(server, sender_email, recipient_email, subject, message, attachment_paths=None):
        email = EmailMessage()
        email['From'] = sender_email
        email['To'] = recipient_email
        email['Subject'] = subject
        email.set_content(message)

        if attachment_paths:
            for attachment_path in attachment_paths.split(';'):
                attachment_path = attachment_path.strip()
                if os.path.exists(attachment_path):
                    with open(attachment_path, 'rb') as file:
                        attachment_data = file.read()
                        attachment_filename = os.path.basename(attachment_path)
                        email.add_attachment(attachment_data, maintype='application', subtype='octet-stream', filename=attachment_filename)
                else:
                    print(f"Attachment not found: {attachment_path}")

        server.send_message(email)

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    server_login_mail = get_email[0]['email']
    server_login_password = get_email[0]['password']
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(server_login_mail, server_login_password)

    recipient_email = recieverem
    attachment_paths = rf'{attach}'
    send_email(server, server_login_mail, recipient_email, subject, msg, attachment_paths)

    server.quit()
    return "success"


@blueprint.route('/saveemail',methods=['GET','POST'])
@login_required
def download():
    email=request.form.get('email')
    passw=request.form.get('password')
    print(email)
    print(passw)
    new_data = {
        'id': len(emailsdata['emails']['data']) + 1,
        'email': email,
        'password': passw,
        'author': str(current_user)
    }
    emailsdata['emails']['data'].append(new_data)
    
    addemail(emailsdata)
    return redirect(url_for('home_blueprint.route_template', template='index'))

@blueprint.route('/emailmarketing',methods=['GET','POST'])
@login_required
def emailmarketing():
    image = request.files['emaildata']
    email=request.form.get('searchcontent')
        
    get_email = [doc for doc in emailsdata['emails']['data'] if doc['email']==str(email)]
    
    
    print(f'{image.filename}')
    
    image.save(f'apps/static/files/{image.filename}')
    
    current_directory = os.getcwd()
    print(current_directory)
    new=os.path.join(current_directory,'apps')
    
    print(new)
    
    pathp=os.path.abspath(f'apps/static/files/{image.filename}')
    
    def send_email(server, sender_email, recipient_email, subject, message, attachment_paths=None):
        email = EmailMessage()
        email['From'] = sender_email
        email['To'] = recipient_email
        email['Subject'] = subject
        email.set_content(message)

        if attachment_paths:
            for attachment_path in attachment_paths.split(';'):
                attachment_path = attachment_path.strip()
                if os.path.exists(attachment_path):
                    with open(attachment_path, 'rb') as file:
                        attachment_data = file.read()
                        attachment_filename = os.path.basename(attachment_path)
                        email.add_attachment(attachment_data, maintype='application', subtype='octet-stream', filename=attachment_filename)
                else:
                    print(f"Attachment not found: {attachment_path}")

        server.send_message(email)

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    server_login_mail = get_email[0]['email']
    server_login_password = get_email[0]['password']

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(server_login_mail, server_login_password)

    with open(pathp, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row)
            recipient_email = row['Email']
            subject = row['Subjects']
            message = row['messages']
            attachment_paths = row['Attachments']
            inserdata(recipient_email,subject,f'{message}'[0:200],'sent')

            send_email(server, server_login_mail, recipient_email, subject, message, attachment_paths)
            
    server.quit()

    
    return redirect(url_for('home_blueprint.route_template', template='index'))

# @blueprint.route('/<template>')
# @login_required
# def route_template(template):

#     try:

#         if not template.endswith('.html'):
#             template += '.html'

#         # Detect the current page
#         segment = get_segment(request)

#         # Serve the file (if exists) from app/templates/home/FILE.html
#         return render_template("home/" + template, segment=segment)

#     except TemplateNotFound:
#         return render_template('home/page-404.html'), 404

#     except:
#         return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
