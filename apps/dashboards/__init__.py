from flask_admin.contrib import rediscli
from flask_admin.contrib import sqla

from flask_admin import Admin, AdminIndexView as _AdminIndexView
from flask_security import current_user
from redis import Redis

from apps import app
from apps.extensions import security
from flask_admin import helpers as admin_helpers
from flask import  request, redirect, abort
# from flask import url_for as flask_url_for
from flask_s3 import url_for



class AdminIndexView(_AdminIndexView):
    """
    admin index view
    """

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.is_accesible_admin():
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                print(current_user.is_authenticated)
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


admin = Admin(name="admin", index_view=AdminIndexView(), endpoint='admin', url='/admin')





@security.context_processor
def security_context_processor():
    return dict(
            admin_base_template=admin.base_template,
            admin_view=admin.index_view,
            h=admin_helpers,
            get_url=url_for
    )


# from . import services, customer
from . import services


redis_host = app.config['REDIS_SESSION_HOST']
redis_port = app.config['REDIS_SESSION_PORT']
redis_password = app.config['REDIS_SESSION_PASSWORD']
redis_db = app.config['REDIS_SESSION_DB']
admin.add_view(rediscli.RedisCli(Redis(host=redis_host, port=redis_port, db=redis_db, password=redis_password),"Redis"))

