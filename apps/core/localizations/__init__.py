from flask import Blueprint, request, g

from apps import app
from apps.extensions import babel

locale_app = Blueprint("locale_app", __name__)


@babel.localeselector
def get_locale():
    lang_code = request.cookies.get('locale_lang')

    if not lang_code in app.config['LANGUAGES'].keys():
        return request.accept_languages.best_match(app.config['LANGUAGES'].keys())
    else:
        return lang_code


@babel.timezoneselector
def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone
