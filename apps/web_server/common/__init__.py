from flask import Blueprint

common_blueprint = Blueprint('web_common', __name__)

from . import controllers
