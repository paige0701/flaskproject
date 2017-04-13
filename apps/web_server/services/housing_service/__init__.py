from flask import Blueprint

housing_blueprint = Blueprint("housing", __name__, url_prefix='/housing')

from . import controllers


