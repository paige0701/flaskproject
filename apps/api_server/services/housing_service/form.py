from wtforms import Form, StringField, validators, TextAreaField
from wtforms.fields.html5 import DateField



class SearchForm(Form):
    keyword = StringField('Keyword', [validators.Length(min=2, max=50)])


class ReservationForm(Form):
    user_name = StringField('Name', [validators.Length(min=2, max=50)])
    email = StringField('Email', [validators.Length(min=2, max=50)])
    nationality = StringField('Nationality', [validators.Length(min=2, max=50)])
    mobile_no = StringField('Mobile Number', [validators.Length(min=2, max=50)])
    kakao_id = StringField('Kakao Id', [validators.Length(min=2, max=50)])
    checkin_date = DateField('Check-in Date', format='%Y-%m-%d')
    checkout_date = DateField('Check-out Date', format='%Y-%m-%d')
    comments = TextAreaField('Comments', [validators.Length(min=2, max=160)])


class EnquiryForm(Form):
    user_name = StringField('Name', [validators.Length(min=2, max=50)])
    email = StringField('Email', [validators.Length(min=2, max=50)])
    nationality = StringField('Nationality', [validators.Length(min=2, max=50)])
    mobile_no = StringField('Mobile Number', [validators.Length(min=2, max=50)])
    kakao_id = StringField('Kakao Id', [validators.Length(min=2, max=50)])
    enquiry = TextAreaField('Enquiry', [validators.Length(min=2, max=300)])

