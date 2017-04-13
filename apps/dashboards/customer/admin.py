from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader
from flask_admin.contrib import sqla
from flask_security import current_user

from apps import db
from apps.api_server.auth.models import (User, Role, Partner,partners_users)
from apps.dashboards import admin


class CustomerAdminView(sqla.ModelView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if 'superuser' in current_user.roles or 'staff' in current_user.roles:
            return True

        return False

    can_create = False
    can_edit = True
    can_delete = False
    column_display_pk = True
    can_export = True
    can_view_details = True
    # column action!!
    # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView.column_extra_row_actions
    # column_extra_row_actions = [
    #     LinkRowAction('glyphicon glyphicon-off', 'http://direct.link/?id={row_id}'),
    #     EndpointLinkRowAction('glyphicon glyphicon-test', 'admin.index')
    # ]
    create_modal = True
    # create_modal_template = 'admin/model/modals/create.html'
    edit_modal = True
    # A list of available export filetypes. csv only is default, but any filetypes supported by tablib can be used.
    # Check tablib for https: //github.com / kennethreitz / tablib / blob / master / README.rst for supported types.
    # list에서 편집 가능하게 하는 columns
    # column_editable_list = ( 'confirmed_at', 'country')
    details_modal = True


class UserModelView(CustomerAdminView):
    column_list = ('email', 'country', 'subdivision', 'first_name', 'last_name', 'roles', 'created_at')
    form_columns = ('email', 'country', 'subdivision', 'first_name', 'last_name', 'confirmed_at', 'roles')
    column_searchable_list = ('email', 'first_name', 'last_name','country.printable_name', 'subdivision.name')

    column_filters = ('email', 'country.printable_name','subdivision.name', 'created_at')
    form_ajax_refs = {
        'roles': QueryAjaxModelLoader('roles', db.session, Role, fields=['name', 'description'], page_size=10)
    }
    # form_ajax_refs = {
    #     'roles': {
    #         'fields': ('name', 'description'),
    #         'page_size': 10
    #     }
    # }
    # excel로 export

    column_details_list = ('id', 'email', 'country', 'first_name', 'last_name', 'roles', 'active', 'confirmed_at',
                           'last_login_at', 'current_login_at', 'last_login_ip', 'current_login_ip', 'login_count',
                           'created_at','subdivision',)

    column_export_list = ('id', 'email', 'country', 'first_name', 'last_name', 'roles', 'active', 'confirmed_at',
                          'last_login_at', 'current_login_at', 'last_login_ip', 'current_login_ip', 'login_count',
                          'created_at','subdivision',)


class RoleModelView(CustomerAdminView):
    can_create = True
    can_delete = True
    column_list = ('name', 'description', 'created_at')
    form_columns = ('name', 'description')
    column_searchable_list = ('name', 'description')

class PartnerModelView(CustomerAdminView):
    can_create = True
    can_delete = True
    column_list = ('name','description', 'country', 'business_number','user', 'user.roles' )
    form_columns = ('name', 'description', 'country', 'business_number')
    column_searchable_list = ('name','description','country', 'business_number')

admin.add_view(UserModelView(User, db.session, category="Customer"))

admin.add_view(RoleModelView(Role, db.session, category="Customer"))
admin.add_view(sqla.ModelView(Partner, db.session, category="Customer"))
