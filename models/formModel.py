from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, Length
from wtforms.validators import DataRequired, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Login')

class addEditForm(FlaskForm):
    prefix = StringField('Prefix', validators=[DataRequired(), Length(min=2, max=20)])
    country_code = StringField('Country Code', validators=[DataRequired(), Length(min=2, max=2)])
    region_code = StringField('Region Code', validators=[DataRequired(), Length(min=2, max=20)])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=20)])
    postal_code = StringField('Postal Code', validators=[DataRequired(), Length(min=2, max=10)])
    submit = SubmitField('Add or Edit')
