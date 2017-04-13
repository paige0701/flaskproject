from wtforms import Form, StringField, validators, TextAreaField,RadioField, BooleanField, IntegerField, SelectField
from wtforms.fields.html5 import DateField
from flask_babel import lazy_gettext as _


class CheckoutForm(Form):
    firstname = StringField('First Name', [validators.Length(min=2, max=20, message="Please check your name")])
    lastname = StringField('Last Name', [validators.Length(min=2, max=20, message="Please check your name")])
    email = StringField('Email', [validators.Email(message="Please check your email")])
    phone = StringField('Contact No', [validators.Length(min=10, max=11, message="Please do not include - in your contact number")])
    country_code = SelectField('Country', choices=[('KR', _('Korea'))])
    state = StringField('State', [validators.Length(min=2, max=30, message='Please check you Province')])
    city = StringField('City', [validators.Length(min=2, max=30, message='Please check your address')])
    line1 = StringField('Line1', [validators.Length(min=2, max=30, message='Please check your address')])
    line2 = StringField('Line2', [validators.Length(min=2, max=50, message='Please check your address')])
    comments = TextAreaField('Comments')
    # payment_method = RadioField('Payment Method', choices=[('PayPal', 'PayPal'), ('AliPay', 'AliPay')],
    #                             validators=[validators.input_required()])

    # condition_agree = BooleanField('Condition', validators=[validators.input_required()])



