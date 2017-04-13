from flask_wtf.file import FileRequired, file_required, file_allowed, FileField
from wtforms import StringField, validators, SelectField, DateField, TextAreaField, RadioField, \
    ValidationError, IntegerField
from flask_wtf import Form

from flask_babel import lazy_gettext as _
from wtforms.fields.html5 import EmailField, TelField

from apps import db
from apps.api_server.address.models import Country
from apps.api_server.utils.custom_form.custom_validator import validate_text_type


class AddressForm(Form):
    COUNTRY_CHOICES = [('KR', _('Korea'))]

    first_name = StringField(_('First Name'), description={'placeholder':_('First name in your passport or'
                                                                           ' alien registration card')},
                             validators=[validators.data_required(_('Must match your name in your passport '
                                                                    'or alien registration card'))])

    last_name = StringField(_('Last Name'), description={'placeholder':_('Last name in your passport or'
                                                                         ' alien registration card')},
                            validators=[validators.data_required(_('Must match your name in your passport '
                                                                   'or alien registration card'))])

    # 특이사항 발생시 Email로 보내드립니다.
    email = StringField(_('Email'), description={'help_text': [
        _('If we need to notify you of any matters relating to your services or accounts, we may send an email.')]},
                        validators=[validators.data_required(_('We need your Email'))])
    # 특이사항 발생시 휴대폰으로 연락을 드립니다.
    contact_no = StringField(_('Contact No'), description={'help_text': [_(
        'If we need to notify you of any matters relating to your services or accounts,'
        ' we may send an SMS text message to your mobile phone number.')]})
    country_code = SelectField(_('Country'), choices=COUNTRY_CHOICES, validators=[validators.data_required()])

    state = StringField(_('State'), description={'placeholder': _('eg. Seoul or Jeollabuk-do')},
                        validators=[validators.data_required(_('We need shipping state'))])

    city = StringField(_('City'), description={'placeholder': _('eg. Seoul or 서울시')},
                       validators=[validators.data_required(_('We need the city'))])

    line1 = StringField(_('Line1'), description={'placeholder': _('eg. Gangnam-gu or 강남구')},
                        validators=[validators.data_required(_('We need your address Line1'))])

    line2 = StringField(_('Line2'),
                        description={'placeholder': _('eg. 423, Chorongmaeul-ro 33-gil 103 Ho')},
                        validators=[validators.data_required(_('We need your address Line2'))])
    message = TextAreaField(_("Message to us", description={'placeholder': _('eg. Please leave a comment')}))


class WirelessOrderForm(AddressForm):
    """
    PAYMENT CHOICES
    """
    PAYMENT_CHOICES = [('paypal', 'Paypal'), ('transfer', 'Transfer Money')]

    PHONE_TYPE_CHOICES = [('')]
    phone_type = StringField(_('Phone Type'),
                             # 휴대폰 종류를 정확히 입력해 주셔야합니다. (eg. Iphone6) 휴대폰에 맞도록 sim을 잘라 드립니다.
                             # 일부 기종은 4G 가입이 제한 될 수도 있습니다
                             description={'placeholder': _('eg. IPhone 5s, Galaxy S7'),
                                          'help_text': [_(
                                              'There are two types of SIM card. Please specify the exact name or'
                                              ' model of your phone (e.g. iPhone6s so we can send you the'
                                              ' right SIM CARD for you phone.'),
                                              _('Some mobile phones may not be have an access to 4G.'),
                                          ]},
                             # _('If we need to notify you of any matters re'
                             #                    'lating to your services or accounts, we may send an email.')

                             validators=[validators.data_required(_('Please write your mobile phone model accurately.'))])

    payment_method = RadioField(_('Payment Method'), description={'placeholder': _('Select payment method')},
                                choices=PAYMENT_CHOICES,
                                validators=[validators.data_required(_('Select Payment Method'))])


class WirelessActivationForm(Form):
    """
    Activation
    """
    PLAN_CHOICES = [('297', 'E Plan'), ('585', 'U Plan'), ('payg', 'P Plan')]

    try:
        nation_list = db.session.query(Country.iso_3166_1_a2, Country.printable_name).order_by('printable_name').all()
    except:
        nation_list = None

    subscriber_info = ['english_name', 'id_number', 'birthday', 'contact_no', 'address', 'nationality']
    service_info = ['call_plan', 'phone_model', 'imei', 'usim_number', 'passport']

    english_name = StringField(_('Name'),
                               description={'placeholder': _('Full name in your Passport or Alien Registration Card'),
                                            'help_text': [
                                                _('Must match your name in your passport '
                                                  'or alien registration card')
                                            ]},
                               validators=[validators.data_required(_('Must match your name in your passport '
                                                                      'or alien registration card'))])

    id_number = StringField(_('Id number'),
                            description={'placeholder': _('eg. 000011233212'),
                                         'help_text': [
                                             _('Passport number or Alien registration number'),
                                             _('Please do not include - in the number')
                                         ]},
                            validators=[validators.data_required(_('This is a required field'))])

    birthday = StringField(_('Date of Birth'),
                           description={'placeholder': _('eg. 19920305'),
                                        'help_text': [
                                            _('Insert 8 digits <br/> If your birthday is 1st of July 1991, '
                                              'please insert 19910701')
                                        ]},
                           validators=[validators.data_required(_('Date of birth YYYY/MM/DD')),
                                       validators.length(min=8,max=8, message=_('Please insert 8 digits YYYY/MM/DD') ),
                                       validate_text_type('number', message='Numbers only')])

    contact_no = TelField(_('Contact Number'),
                          description={'help_text': [
                              _('Please insert contact number')
                          ]},
                          validators=[validators.data_required(_('This is a required field'))])

    address = StringField(_('Address'),
                          description={'placeholder': _(
                              'eg. 서울특별시 강남구 선릉로 13 캠퍼타워팰리스 A동 103호 or 103, Seolleung-ro, Gangnam-gu, Seoul'),
                              'help_text': [_('Please write your address in Korean or english')]},
                          validators=[validators.data_required(_('This is a required field'))])

    nationality = SelectField(_('Nationality'), choices=nation_list,
                              description={
                                  'help_text': [_('We need nationality to check your identification')]},
                              validators=[validators.data_required('This is a required field')])

    call_plan = RadioField(_('Call PLAN'), choices=PLAN_CHOICES,
                           description={'help_text': [_('Please select carefully. When activated, you cannot change the plan')]},
                           validators=[validators.data_required('This is a required field')])

    phone_model = StringField(_('Phone Model'),
                              description={'placeholder': _('eg. Iphone5'), 'help_text': [_('Please insert accurate model name/no')]},
                              validators=[validators.data_required('This is a required field')])
    imei = StringField(_('IMEI Number'),
                       description={'placeholder': _('99212312312'),
                                    'help_text': [_('IMEI number in your settings')]},
                       validators=[validators.data_required('This is a required field')])
    usim_number = StringField(_('Serial Number/Usim Number'),
                              description={'placeholder': _('SIM serial number'),
                                           'help_text': [_('Number on the SIM card')]},
                              validators=[validators.data_required('This is a required field')])

    passport = FileField(_('Passport/Alien Registration Card'), description={'help_text': [_('Only (bmp, gif, png, jpg) files are allowed')]},
                         validators=[file_required(_('Upload your passport')),
                                     file_allowed(('jpg', 'png', 'pdf', 'jpeg', 'gif', 'JPG', 'PNG', 'PDF', 'JPEG', 'GIF',)
                                                  ,_('Please check your image file'))])


