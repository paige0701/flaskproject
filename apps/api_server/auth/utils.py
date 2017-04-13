from flask_security.utils import encrypt_password
from sqlalchemy.exc import AmbiguousForeignKeysError, IntegrityError

from apps import db, app
from apps.api_server.auth.models import User
from apps.extensions import user_datastore


def create_user(email, password, first_name=None, last_name=None, country=None):
    user_datastore.create_user(email=email, password=encrypt_password(password),
                               first_name=first_name, last_name=last_name, country=country)
    db.session.commit()


def create_superuser(email, password):
    role = user_datastore.find_or_create_role(name='superuser')
    if not hasattr(role, '__iter__'):
        roles = [role]
    else:
        roles = role

    user = None

    try:
        user = user_datastore.create_user(email=email, password=encrypt_password(password), roles=roles)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        app.logger.warning("계정 생성 실패")
        app.logger.warning(e)

        return user
    return user


# AmbiguousForeignKeysError


# import json
#
# from flask import jsonify, url_for, request, session, render_template
# from flask_security.utils import encrypt_password
# from flask_security import auth_token_required, http_auth_required
#
# from apps import app, db
# from apps.extensions import user_datastore
# from flask_bcrypt import generate_password_hash, check_password_hash
#
#
# @app.route('/test_login', methods=['GET', 'POST'])
# def test_login():
#     print("AA")
#     user_id = request.form['user_id']
#     password = request.form['password']
#     print(user_id)
#     return jsonify(user_id=user_id, password=password)
#
#
# @app.route('/dummy-api/', methods=['GET'])
# @auth_token_required
# def dummyAPI():
#     ret_dict = {
#         "Key1": "Value1",
#         "Key2": "value2"
#     }
#     return jsonify(items=ret_dict)
#
#
# @app.before_request
# def make_session_permanent():
#     session.permanent = True
#
#
# def create_user():
#     password = encrypt_password("kamp12!!")
#     print(password)
#     print(generate_password_hash("kamp12!!"))
#
#     print(user_datastore.create_user(email='kamper@kamper.co.kr', password=password))
#     print(user_datastore.create_role(name='kamper'))
#     db.session.commit()
#     print(json.dumps({'email': 'test@example.com', 'password': 'test123'}))
#
# # @app.route('/login')
# # def login():
# #     pass
# #     # def login():
# #     #     pass

def updatefirstname(userid,firstname):

    user = User.query.filter(User.id==userid).first()
    user.first_name = firstname

    db.session.add(user)
    db.session.commit()

    return user

def updatelastname(userid,lastname):

    user = User.query.filter(User.id==userid).first()
    user.last_name= lastname

    db.session.add(user)
    db.session.commit()

    return user

def updatenumber(userid,number):

    user = User.query.filter(User.id==userid).first()
    user.contact_number= number

    db.session.add(user)
    db.session.commit()

    return user
