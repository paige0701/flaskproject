from flask import render_template

from apps.web_server.services.catalogue_service import catalogue_blueprint


@catalogue_blueprint.route('/')
def catalogue_all():
    return render_template('catalogue/main.html')

