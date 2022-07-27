from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField,FileField
from wtforms.validators import DataRequired,Length, Email,EqualTo

class ContactForm(FlaskForm):
    fullname = StringField("Fullname", validators=[DataRequired(message="Please ensure that your fullname is longer than 5 characters."),Length(min=5)])
    email = StringField("Email", validators=[Email(message='Please enter a valid email address')])
    password = PasswordField()
    message = TextAreaField()
    submit = SubmitField("Submit")

class SignupForm(FlaskForm):
    firstname = StringField("Firstname", validators=[DataRequired(message="Please enter your first name.")])
    lastname = StringField("Lastname", validators=[DataRequired(message="Please enter your Last name.")])
    email = StringField("Email", validators=[DataRequired(message="Please enter a valid email address")])
    image = FileField()
    password = PasswordField("Password", validators=[DataRequired(message="Please ensure that your password is at 5 characters long"),Length(min=5)])
    cpassword = PasswordField("Confirm Password", validators=[EqualTo("password")])
    submit = SubmitField("Submit")
