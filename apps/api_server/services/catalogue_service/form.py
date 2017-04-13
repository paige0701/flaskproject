from flask import session, request
from flask_security import current_user
from wtforms import StringField, validators, TextAreaField, IntegerField, SelectField
from wtforms import ValidationError
from wtforms.fields.html5 import DateField

from flask_wtf import Form as _Form

from wtforms import Form
from flask_babel import lazy_gettext as _

from apps.api_server.payment.models import OrderLineItem
from apps.api_server.services.catalogue_service.models import CatalogueProduct


def check_quantity(form, field):
    product_detail_no = session.get('product_detail_no')
    print(product_detail_no)

    if not product_detail_no:
        print("session is invalid")

    else:
        print("ddd")
        product = CatalogueProduct.query.filter(CatalogueProduct.id == product_detail_no).first()
        quant = product.quantity
        print(quant)
        print(field.data)
        if quant < field.data:
            raise ValidationError('Name must be less than 50 characters')


def check_return_quantity(form, field):

    order_id = session['return_order_id']
    product_id = session['return_product_id']
    input_quantity = request.form['quantity']
    userid = current_user.id

    line = OrderLineItem.query.filter(OrderLineItem.product_id==product_id,OrderLineItem.order_id==order_id,OrderLineItem.user_id==userid).all()
    print(line)

    for x in line:
        print(x.quantity)
        if int(input_quantity) > int(x.quantity):
            raise ValidationError('Quantity must be less than already bought items')




class ProductDetailForm(_Form):
    quantity = IntegerField('Quantity', [validators.NumberRange(min=1), check_quantity])


def cart_check_quantity(form, field):
    print("cart_update")
    product_no = request.form.getlist("num")
    # for x in product_no:
    #     print(x)


class CartUpdateForm(Form):
    cart_quantity = IntegerField('cart_quantity', [validators.NumberRange(min=1), cart_check_quantity])


class ProductRefundForm(_Form):
    REFUND = [('DA', _('Item is damaged')),
              ('OR', _('Ordered wrong size/style/colour')),
              ('DE', _('Defective')),
              ('WR', _('Wrong item was sent')),
              ('SA', _('Item is not satisfactory')),
              ]

    CHOICE = [('EX', _('Exchange')),
              ('RE', _('Refund')),

              ]

    exchange_refund = SelectField(_('Choose 1?'), choices=CHOICE, validators=[validators.data_required()])

    quantity = IntegerField('Quantity', validators=[validators.data_required(),validators.NumberRange(min=1),
                                                    check_return_quantity],
                            description={'help_text': [_('Please insert quantity of returning item.')]})

    refund_reason = SelectField(_('Reason?'), choices=REFUND,
                                validators=[validators.data_required()])

    email = StringField('Email', [validators.data_required(),validators.Email(message="Please check your email")])

    contact_number = StringField('Contact No', [validators.data_required(),
                                                validators.Length(min=10, max=11,
                                                                  message="Please do not include - "
                                                                          "in your contact number")],
                                 description={'help_text': [_('Please do not include - in your contact number.')]})

    message = TextAreaField(_("Message to us", description={'placeholder': _('eg. Please write any message to us')}))
