from flask import Blueprint
from flask_restful import Resource, url_for

auth_app = Blueprint(name="auth_app", import_name=__name__, template_folder="templates")

