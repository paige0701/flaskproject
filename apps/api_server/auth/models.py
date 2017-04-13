from flask_security import RoleMixin, UserMixin

from apps import db
from apps.api_server.utils.abstract_models import BaseModel

roles_users = db.Table('auth_roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('auth_users.id'), primary_key=True),
                       db.Column('role_id', db.Integer(), db.ForeignKey('auth_roles.id'), primary_key=True))

partners_users = db.Table('auth_partners_users',
                          db.Column('user_id', db.Integer(), db.ForeignKey('auth_users.id'), primary_key=True),
                          db.Column('partner_id', db.Integer(), db.ForeignKey('auth_partners.id'), primary_key=True))


class User(BaseModel, UserMixin):
    __tablename__ = 'auth_users'

    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    contact_number = db.Column(db.String(15))

    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    # Why 45 characters for IP Address ?
    # See http://stackoverflow.com/questions/166132/
    # maximum-length-of-the-textual-representation-of-an-ipv6-address/166157#166157

    last_login_ip = db.Column(db.String(45))
    current_login_ip = db.Column(db.String(45))
    login_count = db.Column(db.Integer)

    country_code = db.Column(db.ForeignKey('address_country.iso_3166_1_a2'), nullable=True)
    country_subdivision_code = db.Column(db.ForeignKey('address_country_subdivision.code'), nullable=True)

    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    country = db.relationship('Country', backref=db.backref('users', lazy='dynamic'), foreign_keys=[country_code])
    subdivision = db.relationship('CountrySubdivision', backref=db.backref('users', lazy='dynamic'),
                                  foreign_keys=[country_subdivision_code])

    def __repr__(self):
        return '<User %r>' % self.email

    def get_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def is_accesible_admin(self):
        if self.roles:
            return True
        else:
            return False


class Role(BaseModel, RoleMixin):
    __tablename__ = 'auth_roles'

    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return '<Role %r>' % self.name


class Partner(BaseModel):
    __tablename__ = 'auth_partners'

    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255))
    country = db.Column(db.String(3))
    business_number = db.Column(db.String(100))

    user = db.relationship('User', secondary=partners_users,
                           backref=db.backref('partner', lazy='dynamic'))

    def __repr__(self):
        return '<Partner %r>' % self.name
