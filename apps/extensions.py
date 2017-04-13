# register extensions
from apps import db, app

import pycountry


"""
extensions
"""

from flask_babel import Babel

babel = Babel()

from flask_security import Security, SQLAlchemyUserDatastore
from apps.api_server.auth.models import User, Role

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
# security는 여기서 등록을 해줘야합니다
from apps.security.forms import KamperLoginForm, KamperRegisterForm

# LoginForm 커스터마이징
security = Security(app, user_datastore, login_form=KamperLoginForm, register_form=KamperRegisterForm)

from flask_marshmallow import Marshmallow

ma = Marshmallow()

from flask_mail import Mail
mail = Mail()


from flask_s3 import FlaskS3
static_s3 = FlaskS3()

from flask_session import Session
sess = Session()

from .utils.thumbnail import Thumbnail
thumbnail = Thumbnail()
