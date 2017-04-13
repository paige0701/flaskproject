from sqlalchemy.ext.hybrid import hybrid_property

from apps import db
from apps.api_server.utils.abstract_models import BaseModel


class Country(db.Model):
    __tablename__ = 'address_country'

    """
       International Organization for Standardization (ISO) 3166-1 Country list.

       The field names are a bit awkward, but kept for backwards compatibility.
       pycountry's syntax of alpha2, alpha3, name and official_name seems sane.
    """
    iso_3166_1_a2 = db.Column(db.CHAR(length=2), primary_key=True)
    iso_3166_1_a3 = db.Column(db.CHAR(length=3), nullable=True)
    iso_3166_1_numeric = db.Column(db.CHAR(length=3), nullable=True)

    #: The commonly used name; e.g. 'United Kingdom'
    printable_name = db.Column(db.String(128))

    #: The full official name of a country
    #: e.g. 'United Kingdom of Great Britain and Northern Ireland'
    # <official name>
    name = db.Column(db.String(128))

    # 'Higher the number, higher the country in the list.'
    display_order = db.Column(db.SmallInteger, default=0, index=True)

    is_shipping_country = db.Column(db.Boolean(), default=False, index=True)

    def __repr__(self):
        return self.printable_name or self.name


    @property
    def code(self):
        """
        Shorthand for the ISO 3166 Alpha-2 code
        """
        return self.iso_3166_1_a2

    @property
    def numeric_code(self):
        """
        Shorthand for the ISO 3166 numeric code.

        iso_3166_1_numeric used to wrongly be a integer field, but has to be
        padded with leading zeroes. It's since been converted to a char field,
        but the database might still contain non-padded strings. That's why
        the padding is kept.
        """
        return u"%.03d" % int(self.iso_3166_1_numeric)


class CountrySubdivision(db.Model):
    __tablename__ = 'address_country_subdivision'

    code = db.Column(db.String(20), primary_key=True)
    type = db.Column(db.String(100))
    name = db.Column(db.String(100))

    iso_3166_country = db.Column(db.ForeignKey('address_country.iso_3166_1_a2'))
    parent_code = db.Column(db.ForeignKey('address_country_subdivision.code'), nullable=True)

    country = db.relationship("Country", backref=db.backref('subdivision'), foreign_keys=[iso_3166_country])
    parent = db.relationship("CountrySubdivision", backref='child_subdivision',
                             foreign_keys=[parent_code], remote_side='CountrySubdivision.code')

    def __repr__(self):
        return "%r in %r" % (self.name, self.iso_3166_country)


class UserAddress(BaseModel):
    __tablename__ = 'address_user_address'

    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))

    iso_3166_country = db.Column(db.ForeignKey('address_country.iso_3166_1_a2'))
    country = db.relationship("Country", foreign_keys=[iso_3166_country])

    state = db.Column(db.String(80))
    city = db.Column(db.String(80))
    line1 = db.Column(db.String(80))
    line2 = db.Column(db.String(80))

    phone = db.Column(db.String(15))
    email = db.Column(db.String(255))
    contact_no = db.Column(db.String(13))

    is_main_shipping =  db.Column(db.Boolean, default=False)
    is_main = db.Column(db.Boolean, default=False)
    is_display = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.ForeignKey('auth_users.id'))
    user = db.relationship('User', backref=db.backref('addresses', lazy='dynamic'), foreign_keys=[user_id])

    @hybrid_property
    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    @hybrid_property
    def full_address(self):
        return "(%s) %s %s %s" % (
            self.country.printable_name, self.state, self.line1, self.line2)

    @staticmethod
    def make_shipping_address(dict_data, user=None, is_main_shipping=False):
        """
        shipping_address를 만든다.
        :param dict_data:
        :param user:
        :param is_main_shipping:
        :return:
        """
        if is_main_shipping:
            for address in user.addresses.filter_by(is_main_shipping=True).all():
                address.is_main_shipping = False
            db.session.commit()
        shipping_address = UserAddress.make_address(dict_data, user, is_main=False)
        shipping_address.is_main_shipping = True

        return shipping_address

    @staticmethod
    def make_address(dict_data, user=None, is_main=False):
        if is_main:
            for address in user.addresses.filter_by(is_main=True).all():
                address.is_main = False
            db.session.commit()
        address = UserAddress(
                first_name=dict_data.get('first_name', None),
                last_name=dict_data.get('last_name', None),
                email=dict_data.get('email', None),
                contact_no=dict_data.get('contact_no', None),
                iso_3166_country=dict_data.get('country_code', None),
                state=dict_data.get('state', None),
                city=dict_data.get('city', None),
                line1=dict_data.get('line1', None),
                line2=dict_data.get('line2', None),
                user=user,
        )
        return address
