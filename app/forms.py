from flask_wtf import Form
from wtforms import StringField, BooleanField, PasswordField, TextAreaField, SelectField, RadioField, IntegerField
from wtforms.validators import DataRequired

class LoginForm(Form):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember me')

class AddFolderForm(Form):
	folder_name = StringField('Folder Name', validators=[DataRequired()])
	keywords = TextAreaField('Keywords', validators=[DataRequired()])

class AddDomainForm(Form):
	domain_name = StringField('Domain Name', validators=[DataRequired()])
	purchase = BooleanField('Purchase Domain', default='checked')
	purchase_privacy = BooleanField('Purchase Privacy', default='checked')
	folder_name = SelectField('Folder Name', coerce=int)
	parker_name = RadioField('Domain Parker\'s name', validators=[DataRequired()],
		choices = [('pk1', 'Parking Crew (SunDial)'), ('pk2', 'Parking Crew (VolumeDirect)'), ('rm', 'Rook Media')])
	contact = SelectField('Contact Name')

class SelectFolderForm(Form):
	folder_name = SelectField('Folder Name', coerce=int)

class SelectAccountForm(Form):
	account_name = SelectField('Account Name')

class ParkingcrewCredsForm(Form):
	account_name = StringField('Parkingcrew Account Name', validators=[DataRequired()])
	username = StringField('Parkingcrew Username', validators=[DataRequired()])
	api_key = StringField('ParkingCrew API Key', validators=[DataRequired()])

class AlpnamesCredsForm(Form):
	account_name = StringField('Alpnames Account Name', validators=[DataRequired()])
	reseller_id = IntegerField('AlpNames Reseller ID', validators=[DataRequired()])
	api_key = StringField('AlpNames API Key', validators=[DataRequired()])
	customer_id = IntegerField('AlpNames Customer ID', validators=[DataRequired()])

class RookmediaCredsForm(Form):
	account_name = StringField('Rookmedia Account Name', validators=[DataRequired()])
	guid = StringField('Rookmedia GUID', validators=[DataRequired()])

class SelectCompanyForm(Form):
	company_name = RadioField('Company name', validators=[DataRequired()], choices = [('pc', 'Parking Crew'), ('rm', 'Rook Media'), ('an', 'Alpnames')])