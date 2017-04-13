from flask_security import LoginForm, RegisterForm
from wtforms import StringField, SelectField
from wtforms.validators import required

from apps import db
from apps.api_server.address.models import Country
from flask_babel import lazy_gettext as _


class KamperLoginForm(LoginForm):
    email = StringField("Email")


class KamperRegisterForm(RegisterForm):
    country_list = db.session.query(Country.iso_3166_1_a2, Country.printable_name).order_by('printable_name').all()

    country_code = SelectField('Country', choices=country_list)
