from sqlite3 import Date
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.fields.core import SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from apps import App
from wtforms.fields.html5 import DateField

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password', validators=[
            DataRequired(), EqualTo('password')])

    # Add new fields        
    name = StringField('Name',
                            validators=[DataRequired(), Length(min=2, max=20)])
    phone = StringField('Phone Number',
                            validators=[DataRequired(), Length(min=2, max=20)])
    address = StringField('Address',
                            validators=[DataRequired()])
    birth = DateField('Date of Birth',
                            format='%Y-%m-%d')
    skills = StringField('Your Skills',
                            validators=[DataRequired()])
    availability = StringField('Availability (hours per day in a week): ',
                               validators=[DataRequired()])
    # End
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        app_object = App()
        mongo = app_object.mongo

        temp = mongo.db.ath.find_one({'email': email.data}, {'email', 'pwd'})
        if temp:
            raise ValidationError('Email already exists!')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    type = SelectField(
        'Login Type', choices=[
            ('Manager', "Manager"), ("Applicant", "Applicant")])
    submit = SubmitField('Login')


class PostingForm(FlaskForm):
    """name = StringField('Your Name: ',
                           validators=[DataRequired(), Length(min=2, max=20)])
    """
    designation = StringField(
        'Job Designation: ', validators=[
            DataRequired(), Length(
                min=2, max=20)])
    job_title = StringField('Job Title: ',
                            validators=[DataRequired()])
    # job_location = StringField('Job Location: ',
    #                            validators=[DataRequired()])
    job_location = SelectField(
        'Job Location', choices=[
            ('Raleigh', "Raleigh"), ("San Jose", "San Jose"), ("New York", "New York"), ("Others", "Others")])
    job_description = StringField('Job Description: ',
                                  validators=[DataRequired()])
    job_type = SelectField(
        'Job Type', choices=[
            ('Full Time', "Full Time"), ("Part Time", "Part Time"), ("Internship", "Internship"), ("Others", "Others")])
    industry = SelectField(
        'Job Type', choices=[
            ('Information Technology', "Information Technology"), ("Business", "Business"), ("Accounting", "Accounting"), ("Others", "Others")])
    skills = StringField('Skills Required: ',
                         validators=[DataRequired()])
    schedule = StringField('Schedule of the job (in hours): ',
                           validators=[DataRequired()])
    salary = StringField('Salary: ',
                         validators=[DataRequired(), Length(min=2, max=20)])
    rewards = StringField('Rewards / Benefits: ',
                          validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('POST')


class ApplyForm(FlaskForm):
    apply_name = StringField(
        'Name', validators=[
            DataRequired(), Length(
                min=2, max=20)])
    apply_phone = StringField(
        'Phone Number', validators=[
            DataRequired(), Length(
                min=2, max=20)])
    apply_address = StringField('Address',
                                validators=[DataRequired()])
    dob = DateField('Date of Birth',
                            format='%Y-%m-%d')
    """position = StringField('Job Position applying for: ',
                           validators=[DataRequired(), Length(min=2, max=100)])
    """
    skills = StringField('Your Skills',
                         validators=[DataRequired()])
    availability = StringField('Availability (hours per day in a week): ',
                               validators=[DataRequired()])
    """resume = StringField('Upload Resume: *****',
                           validators=[DataRequired(), Length(min=2, max=50)])
    """
    signature = StringField('Signature (Full Name)',
                            validators=[DataRequired(), Length(min=2, max=20)])
    schedule = StringField('Schedule',
                           validators=[DataRequired()])
    submit = SubmitField('Submit')


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password', validators=[
            DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset')

class updateProfileForm(FlaskForm):
    apply_name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    apply_phone = StringField('Phone Number', validators=[DataRequired(), Length(min=2, max=20)])
    apply_address = StringField('Address', validators=[DataRequired()])
    dob = DateField('Date of Birth', format='%Y-%m-%d')
    skills = StringField('Your Skills', validators=[DataRequired()])
    availability = StringField('Availability (hours per day in a week)', validators=[DataRequired()])
    submit = SubmitField('Update')