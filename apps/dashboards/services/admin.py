# from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader
# from flask_admin.contrib import sqla
# from flask_security import current_user
#
# from apps import db
#
# from apps.api_server.auth.models import (User, Role, Partner, partners_users)
# # from apps.api_server.services.models import (Service, ServiceType)
# from apps.dashboards import admin
#
# from apps.dashboards.mixins import SuperuserMixIn
#
#
# class CoreServiceAdminView(SuperuserMixIn, sqla.ModelView):
#     """
#     only superuser만 가능
#     """
#     can_create = True
#     can_delete = True
#     column_display_pk = True
#     can_export = True
#     can_view_details = True
#     create_modal = True
#     edit_modal = True
#     details_modal = True
#
#     column_list = ('upc', 'type', 'author', 'partner')
#     form_columns = ('upc', 'type', 'author', 'partner')
#     column_searchable_list = ('upc', 'type.name', 'author.email', 'partner.name')
#     column_filters = ('upc', 'type.name', 'author.email', 'partner.name')
#     form_ajax_refs = {
#         'partner': QueryAjaxModelLoader('partner', db.session, Partner,
#                                         fields=['name', 'description', 'country', 'business_number'], page_size=10),
#         'author': QueryAjaxModelLoader('author', db.session, User,
#                                        fields=['email'])
#     }
#
#     column_details_list = ('upc', 'type', 'author', 'partner',)
#     column_export_list = ('upc', 'type', 'author', 'partner',)
#
#
# class CoreServiceTypeAdminView(SuperuserMixIn, sqla.ModelView):
#     """
#         only superuser만 가능
#     """
#
#     can_create = True
#     can_delete = True
#     column_display_pk = True
#     can_export = True
#     can_view_details = True
#     create_modal = True
#     edit_modal = True
#     details_modal = True
#
#     column_list = ('name', 'description', 'can_delivery',)
#     form_columns = ('name', 'description', 'can_delivery',)
#     column_searchable_list = ('name', 'description', 'can_delivery',)
#     column_filters = ('name', 'description', 'can_delivery',)
#
#     form_ajax_refs = {
#         'services': QueryAjaxModelLoader('services', db.session, Service,
#                                          fields=['upc', 'author', 'partner'], page_size=10)
#     }
#
#     column_details_list = ('name', 'description', 'can_delivery',)
#     column_export_list = ('name', 'description', 'can_delivery',)
#
#
# admin.add_view(CoreServiceTypeAdminView(ServiceType, db.session, name="Core Service Type", category='Service'))
# admin.add_view(CoreServiceAdminView(Service, db.session, name="Core Service", category='Service'))
