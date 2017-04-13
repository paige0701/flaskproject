"""
Register Bluprint, extensions, Error Handler
"""

# Service Register

from flask import render_template

import apps.core.localizations
# Extensions Register
from apps.extensions import (babel, security, user_datastore, mail, static_s3, sess, thumbnail)

# register blueprint core
from apps.api_server import api_bp
from apps.dashboards import admin


# register extensions


def register_extensions(app):
    # Extension을 등록하세요
    babel.init_app(app)

    # security
    # Setup Flask-Security
    admin.init_app(app)
    mail.init_app(app)
    static_s3.init_app(app)
    sess.init_app(app)
    thumbnail.init_app(app)


# Web Server의 blueprint
from apps.web_server.common import common_blueprint
from apps.web_server.services.housing_service import housing_blueprint
from apps.web_server.services.wireless_service import wireless_blueprint
from apps.web_server.services.product_service import product_blueprint


def register_blueprints(app):
    # Blueprint를 등록하세요
    app.register_blueprint(api_bp)
    app.register_blueprint(apps.core.localizations.locale_app)  # locale blueprint

    # Register Web Application
    app.register_blueprint(common_blueprint)
    app.register_blueprint(housing_blueprint)
    app.register_blueprint(wireless_blueprint)

    app.register_blueprint(product_blueprint)

def register_errorhandlers(app):
    # Error handler를 등록하세요
    pass

    def render_error(e):
        return render_template('errors/%s.html' % e.code), e.code

    for e in [401, 404, 500]:
        app.errorhandler(e)(render_error)
