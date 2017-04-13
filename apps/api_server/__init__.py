from flask import Blueprint, render_template, current_app
from flask_restful import Api

from apps import app


version =app.config['API_VERSION']
api_bp = Blueprint('api %s' % version, __name__, url_prefix='/api')
api = Api(api_bp)

# registration

from . import auth, payment
from . import services, basket
from . import address

from .utils.currency import trans_currency




