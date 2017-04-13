from flask_security.forms import ChangePasswordForm as _ChangePasswordForm

from wtforms import Form, StringField, validators, PasswordField
from flask_wtf import Form as _Form

from flask_babel import lazy_gettext as _


class ProfileFirstNameForm(Form):
    firstname = StringField('First Name', [validators.data_required(),
                                           validators.Length(min=2, max=25, message="Must be longer than 2 characters")])


class ProfileLastNameForm(Form):
    lastname = StringField('Last Name', [validators.data_required(),
                                         validators.Length(min=2, max=25, message="Must be longer than 2 characters")])


class ProfileNumberForm(Form):
    contactnumber = StringField('Contact Number',[validators.data_required(),
                                                  validators.Length(min=10, max=11,
                                                                    message="Do not include - in the number")])

# class ChangePasswordForm(_ChangePasswordForm):
#     old_password = PasswordField(_('Old Password'))


