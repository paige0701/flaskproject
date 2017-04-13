from flask_security.utils import encrypt_password
from sqlalchemy.exc import AmbiguousForeignKeysError, IntegrityError
from datetime import datetime
from flask import render_template
from apps import db, app
from .models import Housing, Room, Type, Reservation, Enquiry


def add_housing(housing_type, name, address, thumbnail_image, x_axis, y_axis, description, author_id, partner_id):
    housing = Housing(housing_type, name, address, thumbnail_image, x_axis, y_axis, description, author_id, partner_id)
    db.session.add(housing)
    db.session.commit()


# def add_housing_type(created_at,modified_at,type):
#     type = Type(datetime, datetime ,'')


# Housing 예약 하면 insert 되는 테이블
def add_housing_reservation(room_id, user_id, user_name, email, checkin_date, checkout_date, comments, nationality,
                            kakao_id=None, mobile_no=None):

    reservation = Reservation(room_id=room_id, user_id=user_id, user_name=user_name, email=email,
                              checkin_date=checkin_date, checkout_date=checkout_date, comments=comments, nationality=nationality,
                              kakao_id=kakao_id, mobile_no=mobile_no)
    print(reservation)
    db.session.add(reservation)
    db.session.commit()


# Housing 문의 하면 insert 되는 테이블
def add_housing_enquire(room_id, user_id, user_name, email, enquiry, nationality,
                        kakao_id=None, mobile_no=None):

    enquiry = Enquiry(room_id=room_id, user_id=user_id, user_name=user_name, email=email,
                      enquiry= enquiry,  nationality=nationality,
                      kakao_id=kakao_id, mobile_no=mobile_no)
    print(enquiry)
    db.session.add(enquiry)
    db.session.commit()
