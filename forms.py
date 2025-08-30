from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, FloatField, DateField, TimeField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    user_type = SelectField('I am a', choices=[('provider', 'Service Provider'), ('seeker', 'Service Seeker')])

class RegisterForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    user_type = SelectField('I am a', choices=[('provider', 'Service Provider'), ('seeker', 'Service Seeker')])

class ServiceForm(FlaskForm):
    title = StringField('Service Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    rate = FloatField('Hourly Rate (₹)', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('cleaning', 'House Cleaning'),
        ('cooking', 'Cooking'),
        ('gardening', 'Gardening'),
        ('babysitting', 'Babysitting'),
        ('eldercare', 'Elder Care'),
        ('petcare', 'Pet Care')
    ])

class BookingForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    time_slot = SelectField('Time Slot', choices=[
        ('morning', '9:00 AM - 12:00 PM'),
        ('afternoon', '1:00 PM - 4:00 PM'),
        ('evening', '5:00 PM - 8:00 PM')
    ])

class AvailabilityForm(FlaskForm):
    day_of_week = SelectField('Day', choices=[
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday')
    ], coerce=int)
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    is_available = BooleanField('Available')