from datetime import datetime, timedelta
from types import MethodDescriptorType
# from bson.objectid import ObjectId

from flask_wtf import form
from utilities import Utilities
from flask import app, render_template, session, url_for, flash, redirect, request, Response, Flask
from flask_pymongo import PyMongo
from flask import json
from flask.helpers import make_response
from flask.json import jsonify
from flask_mail import Mail, Message
import jwt
from forms import ForgotPasswordForm, RegistrationForm, LoginForm, ResetPasswordForm, PostingForm, ApplyForm, updateProfileForm
import bcrypt
#from apps import App
from flask_login import LoginManager, login_required
from bson.objectid import ObjectId
from sendmail import Sendemail
import database

app = Flask(__name__)
app.secret_key = 'secret'
#app.config['MONGO_URI'] = 'mongodb+srv://wolfjobs:W00FW00F@cluster0.uj4oftq.mongodb.net/?retryWrites=true&w=majority'
#mongo = PyMongo(app)
mongo = database

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "bogusdummy123@gmail.com"
app.config['MAIL_PASSWORD'] = "helloworld123!"
mail = Mail(app)

@app.route("/")
@app.route("/home")
def home():
############################ 
# home() function displays the homepage of our website.
# route "/home" will redirect to home() function. 
# input: The function takes session as the input 
# Output: Out function will redirect to the login page
# ########################## 
    if session.get('email'):
        return render_template('home.html')
    else:
        return redirect(url_for('login'))


@app.route("/about")
def about():
# ############################ 
# about() function displays About Us page (about.html) template
# route "/about" will redirect to home() function. 
# ########################## 
    return render_template('about.html', title='About')


# @app.route("/register", methods=['POST'])
@app.route("/register", methods=['GET', 'POST'])
def register():
# ############################ 
# register() function displays the Registration portal (register.html) template
# route "/register" will redirect to register() function.
# RegistrationForm() called and if the form is submitted then various values are fetched and updated into database
# Input: Username, Email, Password, Confirm Password
# Output: Value update in database and redirected to home login page
# ########################## 
    if not session.get('email'):
        form = RegistrationForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                username = request.form.get('username')
                email = request.form.get('email')
                password = request.form.get('password')

                name = request.form.get('name')
                phone = request.form.get('phone')
                address = request.form.get('address')
                birth = request.form.get('birth')
                skills = request.form.get('skills')
                availability = request.form.get('availability')

                id = mongo.db.ath.insert_one({'name': username, 'email': email, 'pwd': bcrypt.hashpw(
                    password.encode("utf-8"), bcrypt.gensalt()), 'temp': None, 'legal_name': name, 
                    'phone': phone, 'address': address, 'birth': birth, 'skills': skills, 'availability': availability})

                mongo.db.savedJobs.insert_one({'email': email, 'savedJobs': []})
                # Send alerting email after completing registration
                smtp_mail = Sendemail()
                smtp_mail.send_mail_regis(email, name)
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
# ############################ 
# login() function displays the Login form (login.html) template
# route "/login" will redirect to login() function.
# LoginForm() called and if the form is submitted then various values are fetched and verified from the database entries
# Input: Email, Password, Login Type 
# Output: Account Authentication and redirecting to Dashboard
# ########################## 
    if not session.get('email'):
        form = LoginForm()
        if form.validate_on_submit():
            temp = mongo.db.ath.find_one({'email': form.email.data}, {
                                         'email', 'pwd', 'temp'})
            if temp is not None and temp['email'] == form.email.data and (
                bcrypt.checkpw(
                    form.password.data.encode("utf-8"),
                    temp['pwd']) or temp['temp'] == form.password.data):
                flash('You have been logged in!', 'success')
                session['email'] = temp['email']
                session['login_type'] = form.type.data
                return redirect(url_for('dashboard'))
            else:
                flash(
                    'Login Unsuccessful. Please check username and password',
                    'danger')
    else:
        return redirect(url_for('home'))
    return render_template(
        'login.html',
        title='Login',
        form=form,
        type=form.type.data)


@app.route("/logout", methods=['GET', 'POST'])
def logout():
# ############################ 
# logout() function just clears out the session and returns success
# route "/logout" will redirect to logout() function.
# Output: session clear 
# ########################## 
    session.clear()
    return "success"


@app.route("/forgotpassword", methods=['POST', 'GET'])
def forgotPassword():
# ############################ 
# forgotpassword() function displays the Forgot Password form (forgotpassword.html) template
# route "/forgotpassword" will redirect to forgotpassword() function.
# ForgotPasswordForm() called and if the form is submitted then email is fetched and verified from the database entries
# if authenticated then a mail with new pasword is sent
# Input: Email
# Output: Account Authentication, Email sent to user and redirecting to Login Page
# ########################## 
    if not session.get('email'):
        form = ForgotPasswordForm()
        if form.validate_on_submit():
            temp = mongo.db.ath.find_one({'email': form.email.data}, {
                                         'email', 'pwd', 'temp'})
            if temp is None:
                flash('Incorrect Email Id', 'danger')
                f = ForgotPasswordForm()
                return render_template('forgotpassword.html', form=f)
            if temp['email'] == form.email.data:
                sendmail = Sendemail()
                sendmail.send_mail_forget_password(form.email.data)
                return redirect(url_for("login"))
            else:
                flash('Incorrect email id', 'danger')

        return render_template("forgotpassword.html", form=form)

    else:
        return redirect(url_for('home'))
    
@app.route("/resetpassword", methods=['POST', 'GET'])
def resetPassword():
    form = ResetPasswordForm()
    print(session.get('email'))
    return render_template("resetpassword.html", form=form)

@app.route("/posting", methods=['GET', 'POST'])
def posting():
# ############################ 
# posting() function displays Job Posting form (job_post.html) template
# route "/posting" will redirect to posting() function.
# PostingForm() called and if the form is submitted then various input values are updated into database
# Input: Job Designation, Job Title, Job Location, Job Description, Skills required, Schedule of the job, Salary, Rewards
# Output: values updated in database and page redirected to dashboard 
# ########################## 
    if session.get('email') is not None and session.get(
            'email') and session.get('login_type') == 'Manager':
        form = PostingForm()
        if form.validate_on_submit():
            now = datetime.now()

            now = now.strftime('%Y-%m-%d %H:%M')

            #name = form.name.data
            email = session['email']
            designation = form.designation.data
            job_title = form.job_title.data
            job_location = form.job_location.data
            job_description = form.job_description.data
            job_type = form.job_type.data
            industry  = form.industry.data
            skills = form.skills.data
            schedule = form.schedule.data
            salary = form.salary.data
            rewards = form.rewards.data

            id = mongo.db.jobs.insert_one({'email': email,
                                       'designation': designation,
                                       'job_title': job_title,
                                       'job_description': job_description,
                                       'time_posted': now,
                                       'job_location': job_location,
                                       'job_type': job_type,
                                       'industry': industry,
                                       'skills': skills,
                                       'schedule': schedule,
                                       'salary': salary,
                                       'rewards': rewards,
                                       'Appliers': [],
                                       'selected': None})
            flash("Job Created!", 'success')
            return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))
    return render_template('job_post.html', form=form)


@app.route("/applying", methods=['GET', 'POST'])
def applying():
# ############################ 
# applying() function displays Job application form (apply.html) template
# route "/applying" will redirect to applying() function.
# ApplyForm() called and if the form is submitted then various input values are updated into database
# Input: Name, Phone No., Address, date of birth, skills, Availability, schedule, Signature 
# Output: Values updated in database and page redirected to dashboard 
# ########################## 
    if session.get('email') is not None and session.get(
            'email') and session.get('login_type') == 'Applicant':
        form = ApplyForm()
        if form.validate_on_submit():
            now = datetime.now()

            now = now.strftime('%Y-%m-%d %H:%M')

            name = form.apply_name.data
            email = session['email']
            phone = form.apply_phone.data
            apply_address = form.apply_address.data
            dob = form.dob.data
            skills = form.skills.data
            availability = form.availability.data
            schedule = form.schedule.data

            id = mongo.db.applier.insert_one({'name': name,
                                          'email': email,
                                          'phone': phone,
                                          'apply_address': apply_address,
                                          'dob': dob,
                                          'time_posted': now,
                                          'availability': availability,
                                          'schedule': schedule,
                                          'skills': skills,
                                          'status': 0})
            flash("Job Applied!", 'success')
            return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))
    return render_template('job_post.html', form=form)


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
# ############################ 
# dashboard() function displays the main page of our website (dashboard.html) template. It shows jobs posted and available and applied jobs.
# route "/dashboard" will redirect to dashboard() function.
# Various details of postings and jobs are fetched from database and displayed
# Input: Login type, Email
# Output: various details of postings and jobs
# ########################## 
    login_type = session["login_type"]
    email = session['email']

    if login_type == 'Manager':
        if mongo.db.jobs.find_one({'email': email}) is None:
            return render_template('dashboard.html', jobs=None)
        else:
            cursor = mongo.db.jobs.find({'email': email})
            get_jobs = []
            for record in cursor:
                get_jobs.append(record)

            get_jobs = sorted(
                get_jobs,
                key=lambda i: i['time_posted'],
                reverse=True)
            if(len(get_jobs) > 5):
                return render_template('dashboard.html', jobs=get_jobs[:5])
            else:
                return render_template('dashboard.html', jobs=get_jobs)
    else:
        key_word = ''
        location = ''
        job_type = ''
        industry = ''
        query_dict = {}
        query_dict['email'] = {'$ne': email}
        query_dict['job_title'] = {'$regex': key_word, '$options': 'i'}
        # query_dict = {'email': {'$ne': email}}
        if request.args.get('keyword'):
            key_word = '.*' + request.args.get('keyword') + '.*'
            query_dict['job_title'] = {'$regex': key_word, '$options': 'i'}
        
        if request.args.get('location'):
            location = request.args.get('location')
            if location != 'all':
                query_dict['job_location'] = {'$eq' : location}
        
        if request.args.get('type'):
            job_type = request.args.get('type')
            if job_type != 'all':
                query_dict['job_type'] = {'$eq' : job_type}
        
        if request.args.get('industry'):
            industry = request.args.get('industry')
            if industry != 'all':
                query_dict['industry'] = {'$eq' : industry}
        
        cursor = mongo.db.jobs.find(query_dict)
        savedJobs = mongo.db.savedJobs.find_one({'email': email})
        get_jobs = []
        for record in cursor:
            for appliers in record['Appliers']:
                if appliers == email:
                    record['haveApplied']=True
                    break;
            for job in savedJobs['savedJobs']:
                if job == str(record['_id']):
                    print('true')
                    record['haveSaved']=True
                    break;            
            get_jobs.append(record)

        get_jobs = sorted(
            get_jobs,
            key=lambda i: i['time_posted'],
            reverse=True)
        return render_template('dashboard.html', jobs=get_jobs)

@app.route("/jobDetails", methods=['GET', 'POST'])
def jobDetails():
# ############################ 
# jobDetails() function displays the main page of our website (job_details.html) template. It shows jobs posted and available and applied jobs.
# route "/jobDetails" will redirect to jobDetails() function.
# ApplyForm() called and if the form is submitted then various input values are updated into database
# Input: Login type, Email, job_id
# Output: If applicant - job_details.html is displayed and if manager then all applicants data is displayed along with job details
# ########################## 
    form = ApplyForm()
    email = session['email']
    login_type = session["login_type"]
    job_id = request.args.get("job_id")
    job = mongo.db.jobs.find_one({'_id': ObjectId(job_id)})
    applicant = mongo.db.ath.find_one({'email': email})

    if form.validate_on_submit():
        if request.method == 'POST':
            apply_name = request.form.get('apply_name')
            email = session['email']
            apply_phone = request.form.get('apply_phone')
            apply_address = request.form.get('apply_address')
            dob = request.form.get('dob')
            skills = request.form.get('skills')
            availability = request.form.get('availability')
            schedule = request.form.get('schedule')
            id = mongo.db.applier.insert_one(
                {
                    'job_id': ObjectId(job_id),
                    'email': email,
                    'name': apply_name,
                    'phone': apply_phone,
                    'address': apply_address,
                    'dob': dob,
                    'skills': skills,
                    'availability': availability,
                    'schedule': schedule,
                    'status': 0})
            mongo.db.jobs.update_one({'_id': ObjectId(job_id)}, {
                                 '$push': {'Appliers': session['email']}})
            # Send alerting email after applying a job
            smtp_mail = Sendemail()
            smtp_mail.send_mail_apply(email, apply_name, job['job_title'])
        flash('Successfully Applied to the job!', 'success')
        return redirect(url_for('dashboard'))

    if login_type == "Applicant":

        # print(applicant, file=sys.stdout)
        form.apply_address.data = applicant.get('address')
        form.apply_name.data = applicant.get('legal_name')
        form.apply_phone.data = applicant.get('phone')
        form.dob.data = datetime.strptime(applicant.get('birth'),'%Y-%m-%d')
        form.skills.data = applicant.get('skills')
        form.availability.data = applicant.get('availability')
        
        # Check if applicant fill out profile
        if not (form.apply_address.data and form.apply_name.data and form.apply_phone.data and form.dob.data and form.skills.data and form.availability.data):
            flash('Please complete profile before apply', 'danger')
            return redirect(url_for('updateProfile'))
        else:
            return render_template(
                'job_details.html',
                job=job,
                form=form,
                applicant=applicant)
    else:
        applicant = []
        print(job_id)
        # applicants = mongo.db.applier.find({'job_id': ObjectId(job_id), 'status': {'$lt': 2}})
        applicants = mongo.db.applier.find({'job_id': ObjectId(job_id)})
        for record in applicants:
            record['email_jobid']=record['email']+' '+job_id
            applicant.append(record)
        # print(applicant)
        return render_template(
            'job_details.html',
            job=job,
            applicant=applicant)


@app.route("/deleteJob", methods=['GET', 'POST'])
def deleteJob():
# ############################ 
# deleteJob() function just clears out a particular job with job_id from the databse and returns back to dashboard
# route "/deleteJob" will redirect to deleteJob() function.
# Input: job_id
# Output: particular job with job_id removed and page redirected to dashboard
# ########################## 
    job_id = request.args.get("job_id")
    id = mongo.db.jobs.delete_one({'_id': ObjectId(job_id)})
    return redirect(url_for('dashboard'))


@app.route("/selectApplicant", methods=['GET', 'POST'])
def selectApplicant():
# ############################ 
# selectApplicant() function performs the functionality of seleting an applicant for interview.
# route "/selectApplicant" will redirect to selectApplicant() function.
# Input value are taken and corresponding to those values set attribute is update to selected in database
# Input: job_id, applicant_id
# Output: Applicant is selected (database updated) and page redirected to dashboard
# ########################## 
    job_id = request.args.get("job_id")
    job = mongo.db.jobs.find_one({'_id': ObjectId(job_id)}, {'_id': 0, 'job_title': 1})
    applicant_id = request.args.get("applicant_id")
    email = request.args.get("email")
    applicant = mongo.db.ath.find_one({'email': email}, {'_id': 0, 'legal_name': 1})
    mongo.db.jobs.update_one({'_id': ObjectId(job_id)}, {
        '$set': {"selected": applicant_id}})
    mongo.db.applier.update_one({'email': email, 'job_id': ObjectId(job_id)}, [{'$set': {'status': 2}}])
    # Send interview invitation to selected applicants
    smtp_mail = Sendemail()
    smtp_mail.send_mail_interview(email, job['job_title'], applicant['legal_name'])
    return redirect(url_for('dashboard'))

@app.route("/rejectApplicant", methods=['GET', 'POST'])
def rejectApplicant():
# ############################ 
# rejectApplicant() function performs the functionality of rejecting an applicant for a particular job.
# route "/rejectApplicant" will redirect to rejectApplicant() function.
# Input value are taken and corresponding to those values set attribute is update to selected in database
# Input: job_id, applicant_id
# Output: Applicant is selected (database updated) and page redirected to dashboard
# ########################## 
    job_id = request.args.get("job_id")
    applicant_id = request.args.get("applicant_id")
    email = request.args.get("email")
    applicant = mongo.db.ath.find_one({'email': email}, {'_id': 0, 'legal_name': 1})
    mongo.db.applier.update_one({'email': email, 'job_id': ObjectId(job_id)}, [{'$set': {'status': 3}}])
    # Send reject mail to selected applicants
    smtp_mail = Sendemail()
    smtp_mail.send_mail_reject(email, applicant['legal_name'])
    return redirect(url_for('dashboard'))



@app.route("/jobsApplied", methods=['GET', 'POST'])
def jobsApplied():
# ############################ 
# jobsApplied() function performs the functionality displaying number of jobs an applicant applied to
# route "/jobsApplied" will redirect to jobsApplied() function.
# Input: email and Appliers
# Output: Display of Number of jobs an applicant applied to.
# ########################## 
    email = session['email']
    cursor = mongo.db.applier.find({'email': email}).sort([("status", 1)])
    get_all_jobs = []
    for record in cursor:
        job = mongo.db.jobs.find_one({'_id': ObjectId(record['job_id'])})
        if record['status']==0:
            job['status']='waiting to be reviewed'
        elif record['status']==1:
            job['status']='under review'
        elif record['status']==2:
            job['status']='accepted to be interviewed'
        elif record['status']==3:
            job['status']='rejected'
        
        get_all_jobs.append(job)
    if get_all_jobs == []:
        return render_template('jobs_applied.html', status=False)
    else:
        return render_template('jobs_applied.html',
                               jobs=get_all_jobs, status=True)

@app.route("/jobsSaved", methods=['GET', 'POST'])
def jobsSaved():
# ############################ 
# ########################## 
    email = session['email']
    cursor = mongo.db.savedJobs.find_one({'email': email})

    get_all_jobs = []
    for job_id in cursor['savedJobs']:
        job = mongo.db.jobs.find_one({'_id': ObjectId(job_id)});
        for appliers in job['Appliers']:
            if appliers == email:
                job['haveApplied']=True;
                break;
        get_all_jobs.append(job)
    if get_all_jobs == []:
        return render_template('jobs_saved.html', status=False)
    else:
        return render_template('jobs_saved.html',
                               jobs=get_all_jobs, status=True)

@app.route('/doSaveOrRemoveJob', methods=['POST', 'GET'])
def doSaveOrRemoveJob():
    email = session['email']
    if request.method == "POST":
        data = request.get_json();
        if data['isSave']:
            mongo.db.savedJobs.update_one({'email': email}, {
                                 '$push': {'savedJobs': data['job_id']}})
        else:
            mongo.db.savedJobs.update_one({'email': email}, {
                                 '$pull': {'savedJobs': data['job_id']}})

    results = {'isSaved': bool(data['isSave'])}
    return jsonify(results)

@app.route('/changeJobStatus', methods=['POST', 'GET'])
def changeJobStatus():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        mongo.db.applier.update_one({'email': data['email'], 'job_id': ObjectId(data['job_id'])}, [{'$set': {'status': data['status']}}])
    results = {'isSuccess': True}
    return jsonify(results)

@app.route("/dummy", methods=['GET'])
def dummy():
# ############################ 
# dummy() function performs the functionality displaying the message "feature will be added soon"
# route "/dummy" will redirect to dummy() function.
# Output: redirects to dummy.html
# ########################## 
    """response = make_response(
                redirect(url_for('home'),200),
            )
    response.headers["Content-Type"] = "application/json",
    response.headers["token"] = "123456"
    return response"""
    return render_template('dummy.html')

@app.route("/update_profile", methods=['GET', 'POST'])
def updateProfile():
# ############################ 
# updateProfile() function performs the functionality of updating personal profile
# route "/update_profile" will redirect to updateProfile() function.
# Output: if login_type is 'Applicant', redirects to update_profile.html 
#         otherwise, redirects to dashboard.
# ########################## 

    form = updateProfileForm()
    email = session['email']
    login_type = session["login_type"]
    applicant = mongo.db.ath.find_one({'email': email})
   
    if form.validate_on_submit():
        if request.method == 'POST':        
            name = request.form.get('apply_name')
            # email = request.form.get('email')
            phone = request.form.get('apply_phone')
            address = request.form.get('apply_address')
            birth = request.form.get('dob')
            skills = request.form.get('skills')
            availability = request.form.get('availability')

            mongo.db.ath.update_one({ "_id": ObjectId(str(applicant.get("_id")))},
                                            {'$set': {'legal_name': name, 'phone': phone,
                                            'address': address, 'birth': birth, 'skills': skills, 'availability': availability}})
            print("Profile updated!")

            # Test if database updated

            # applicant = mongo.db.ath.find_one({'email': email})
            # print('after update: ')
            # print(applicant)

        flash(f'Profile for {applicant.get("name")} has been updated', 'success')
        return redirect(url_for('updateProfile'))

    if login_type == 'Applicant':

        # print('before update: ')
        # print(applicant)
        form.email.data = applicant.get('email')
        form.apply_address.data = applicant.get('address')
        form.apply_name.data = applicant.get('legal_name')
        form.apply_phone.data = applicant.get('phone')
        form.dob.data = datetime.strptime(applicant.get('birth'),'%Y-%m-%d')
        form.skills.data = applicant.get('skills')
        form.availability.data = applicant.get('availability')

        return render_template('update_profile.html', form=form)

    else:
        flash(f'No profile update needed', 'success')
        return redirect(url_for('dashboard'))
    
if __name__ == '__main__':
    app.run(debug=False)
