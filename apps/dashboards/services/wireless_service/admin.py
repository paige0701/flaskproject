from flask import url_for, redirect, request, flash
from flask_admin.form import Select2Field, Select2Widget
from flask_admin.model.widgets import XEditableWidget
from flask_admin.model.helpers import get_mdict_item_or_list
from flask_admin.helpers import get_redirect_target, get_form_data
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader
from flask_admin.contrib import sqla
from flask_admin import BaseView, expose
from markupsafe import Markup
from werkzeug.exceptions import abort
from wtforms import SelectField, TextField, StringField

from apps import db, app
from apps.api_server.payment.models import Payment
from apps.api_server.services.wireless_service.models import WirelessSimOrder, WirelessSimActivateModel

from apps.dashboards import admin
from apps.dashboards.mixins import StaffMixIn, PartnerMixIn

from flask_babel import lazy_gettext as _, gettext
from flask_security import current_user

from apps.dashboards.utils.custom_fields import CloudImageUploadField, IMAGE_ALLOWED_EXTENSIONS, thumbgen_filename
from apps.utils.file_manager import url_for_s3, get_s3_url


class CustomWidget(XEditableWidget):
    def get_kwargs(self, subfield, kwargs):
        if subfield.type == 'TextAreaField':
            kwargs['data-type'] = 'textarea'
            kwargs['data-rows'] = '20'
        # elif: kwargs for other fields

        return kwargs


class WirelessSimOrderAdmin(StaffMixIn, sqla.ModelView):
    """
        Role에 따른 Authorization
        =============================================
                     | Get | Upt | Del |
        - superuser: | All | All | All |
        - staff:     | All | All | No  |
        - partner:   |Some |Some |Some |
        =============================================
    """
    can_view_details = True
    details_modal = True
    can_create = False
    create_modal = False
    can_edit = False
    edit_modal = False

    # edit_column_name = ('user', 'sim_number')


    can_export = True

    column_list = (
        'full_name', 'shipping_address.email', 'shipping_address.contact_no',
        'full_address', 'phone_type', 'sim_type', 'sim_number',
        'payment', 'order_state', 'message',
    )
    column_labels = {
        'full_name': 'Name',
        'shipping_address.email': 'Email',
        'shipping_address.contact_no': 'Contact',
        'full_address': 'Address',
    }

    @expose('/shipping/<order_id>')
    def start_shipping(self, order_id):
        sort = request.args.get('sort')
        desc = request.args.get('desc')

        return_url = get_redirect_target() or self.get_url('.index_view', sort=sort, desc=desc)
        order = self.model.query.filter_by(id=order_id).first()

        if order.sim_number is None:
            return redirect(return_url)

        if not order:
            return redirect(return_url)

        order.shipping_start()

        db.session.commit()
        return redirect(return_url)

    column_editable_list = ('sim_number',)

    def _order_state_formatter(view, context, model, name):
        order_status_choices = app.config.get('ORDER_STATUS_CHOICES')
        now_sort = request.args.get('sort')
        now_desc = request.args.get('desc')

        if model.order_state == 1:
            return Markup(
                    "%s <a data-pk='%s' data-url='./shipping' class='btn btn-xs' href='%s'>%s</button>"
                    % (order_status_choices[model.order_state][1], model.id,
                       url_for('.start_shipping', order_id=model.id, sort=now_sort, desc=now_desc), "Go to Ship")
            )
        else:
            return "%s" % order_status_choices[model.order_state][1]

    column_formatters = {
        'order_state': _order_state_formatter,

    }


class WirelessSimActivationAdmin(StaffMixIn, sqla.ModelView):
    can_view_details = True
    details_modal = True

    column_list = (
        'english_name', 'id_number', 'birthday', 'contact_no', 'address', 'nationality', 'call_plan', 'phone_model',
        'imei', 'sim_number', 'passport_img', 'sim_type', 'active_number', 'get_status', 'status_description')
    form_overrides = dict(passport_img=CloudImageUploadField)

    form_args = dict(
            passport_img={
                'label': 'ID card',
                'storage_type': 's3',
                'allowed_extensions': IMAGE_ALLOWED_EXTENSIONS,
                'allow_overwrite': False,
                # 자르기 사이즈
                'thumbnail_size': (100, 100, True),
                'endpoint': 'media',
                'relative_path': 'wireless/',
                # 'relative_path':'category',
                'url_relative_path': 'wireless',
                'base_path': 'media',
            },
    )
    column_labels = {
        'get_status': _('Status')
    }

    def _list_thumbnail(view, context, model, name):
        if not model.passport_img:
            return ''
        return Markup('<img style="width:100px; height:100px;" src="%s"' % get_s3_url(filename=model.passport_img,
                                                                                      method='private'))
        # return Markup('<img style="width:100px; height:100px;" src="%s"' % url_for('private_media', filename=model.passport_img))
        # return Markup('<img src="%s">' % url_for_s3('media', filename=thumbgen_filename(model.passport_img)))

        # column format

    column_formatters = {
        'passport_img': _list_thumbnail
    }


admin.add_view(WirelessSimOrderAdmin(WirelessSimOrder, db.session, name='SIM Order', category='Wireless'))
admin.add_view(WirelessSimActivationAdmin(WirelessSimActivateModel, db.session, name='SIM Activation', category='Wireless'))
