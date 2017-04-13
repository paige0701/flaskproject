from flask import Blueprint

catalogue_blueprint = Blueprint("catalogue", __name__, url_prefix='/catalogue')

from . import controller


