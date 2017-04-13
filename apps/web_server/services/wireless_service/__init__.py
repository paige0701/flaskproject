from flask import Blueprint

wireless_blueprint = Blueprint("wireless", __name__, url_prefix='/wireless')

from . import controller


