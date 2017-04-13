from locale import str
from math import cos, sqrt, sin
from xml.etree.ElementTree import PI

import math

from apps import db
from apps.api_server.utils.abstract_models import BaseModel

from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

"""
housing_service에 대한 공공 시설들을 나타내는 테이블
housing에 대한 공공 시설들을 나타냄
"""
housing_service_public_facilities = db.Table('housing_service_public_facilities',
                                             db.Column('housing_service_id', db.Integer(),
                                                       db.ForeignKey('housing_services.id'), primary_key=True),
                                             db.Column('housing_public_facilities_id', db.Integer(),
                                                       db.ForeignKey('housing_public_facilities.id'), primary_key=True))

"""
housing room에 대한 개인 시설들을 나타내는 테이블
housing room과 개인 시설들에 대한 관계를 나타냄
"""
housing_rooms_private_facilities = db.Table('housing_rooms_private_facilities',
                                            db.Column('housing_rooms_id', db.Integer(),
                                                      db.ForeignKey('housing_rooms.id'), primary_key=True),
                                            db.Column('housing_private_facilities_id', db.Integer(),
                                                      db.ForeignKey('housing_private_facilities.id'),
                                                      primary_key=True))


class Housing(BaseModel):
    """
    ** housing_service

    type_id: housing_type_id (FK)  (고시원, 원룸, 레지던스 등)
    name: 이름
    address: 주소
    thumnail_image: 메인 이미지
    latitude: 위도
    longitude: 경도
    description: 설명
    author_id: 작성자 user_id
    partner_id: 파트너사에 대한 아이디
    """
    __tablename__ = 'housing_services'

    housing_type_id = db.Column(db.Integer(), db.ForeignKey('housing_type.id'))
    name = db.Column(db.String(100))
    address1 = db.Column(db.String(200))
    address2 = db.Column(db.String(200))
    latitude = db.Column(db.DECIMAL(10, 6))
    longitude = db.Column(db.DECIMAL(10, 6))
    description = db.Column(db.Text())
    author_id = db.Column(db.Integer(), db.ForeignKey('auth_users.id'))
    partner_id = db.Column(db.Integer(), db.ForeignKey('auth_partners.id'))
    min_rental_period = db.Column(db.Integer())
    author = db.relationship('User', backref=db.backref('housing'))
    partner = db.relationship('Partner', backref=db.backref('housing'))
    housingtype = db.relationship('Type', backref=db.backref('housing'))

    publicfacilities = db.relationship('PublicFacilities', secondary=housing_service_public_facilities,
                                       backref=db.backref('housing'))

    def __repr__(self):
        return '<HousingName %r, Latitude %r, Longitude %r>' % (self.name, self.latitude, self.longitude)

    # 지도에서 좌표 하나 클릭 했을 때 보여지는 말풍선 안에 있는 정보들
    def get_housing_list(self):
        return {
            'name': self.name,
            'address2': self.address2,
            'description': self.description,
            'latitude': self.latitude,
            'longitude': self.longitude
        }

    def housing_detail(self):
        return {
            'name': self.name,
            'address2': self.address2,
            'description': self.description,
            'min_price': self.get_lowest_price(),
            'max_price': self.get_highest_price(),
            'partner_id': self.partner_id
        }

    @hybrid_property
    def get_thumbnail_image(self):
        thumbnail = None
        for img in self.images.all():
            print(img)
            if img.is_thumbnail:
                print('x')
                thumbnail = img
        return thumbnail.url

    @hybrid_property
    def get_images(self):

        if self.images is None:
            return "image_not_found.jpg"
        return self.images.all()

    @hybrid_property
    def get_lowest_price(self):
        """
        service 내에 있는 room중 가장 낮은 가격을 나타냄.
        :return: min_price
        """
        try:
            min_price = 9999999999
            if not self.room:
                return None
            for r in self.room:
                if r.price < min_price:
                    min_price = r.price
        except:
            return None
        return min_price

    @hybrid_property
    def get_highest_price(self):
        """
        service 내에 있는 room중 가장 높은 가격을 나타냄
        :return: max_price
        """
        try:
            max_price = 0
            if not self.room:
                return None
            for r in self.room:
                if r.price > max_price:
                    max_price = r.price
        except:
            raise None

        return max_price

    @hybrid_property
    def get_average_price(self):
        avg_prcie = None
        try:

            if not self.room:
                return None
            total_price = 0
            amount = 0
            for r in self.room:
                total_price += r.price
                amount += 1
            avg_price = total_price / amount

        except:
            return None

        return avg_price


class HousingImage(BaseModel):
    """
    방의 이미지를 저장합니다.
    """
    __tablename__ = 'housing_image'

    housing_id = db.Column(db.Integer(), db.ForeignKey('housing_services.id'))
    url = db.Column(db.String(255))
    is_thumbnail = db.Column(db.Boolean, default=False)

    housing = db.relationship('Housing', backref=db.backref('images', lazy='dynamic'))

    def __repr__(self):
        return '<HousingImage %r>' % self.url


class Type(BaseModel):
    __tablename__ = 'housing_type'

    type = db.Column(db.String(63))

    def __repr__(self):
        return '<Type %r>' % self.type

    def get_type(self):
        return {'type': self.type}


class Room(BaseModel):
    __tablename__ = 'housing_rooms'

    housing_service_id = db.Column(db.Integer(), db.ForeignKey('housing_services.id'))
    name = db.Column(db.String(100))
    description = db.Column(db.Text())
    price = db.Column(db.Integer())
    vacancy = db.Column(db.Integer())
    deposit = db.Column(db.Integer())
    housingservice = db.relationship('Housing', backref=db.backref('room'))

    privatefacilities = db.relationship('PrivateFacilities', secondary=housing_rooms_private_facilities,
                                        backref=db.backref('room'))

    def __repr__(self):
        return '<Room %r>' % self.name

    @hybrid_property
    def get_thumbnail_image(self):
        thumbnail = None
        for img in self.images.all():
            print(img)
            if img.is_thumbnail:
                print('x')
                thumbnail = img
        return thumbnail.url

    @hybrid_property
    def get_images(self):
        return self.images.all()

    # 한 고시원 안에 있는 모든 방 리스트
    def get_room_list(self):
        return {'name': self.name,
                'description': self.description,
                'price': self.price,
                'vacancy': self.vacancy,
                'deposit': self.deposit
                }

    # 방 하나 하나의 디테일들을 가지고 온다
    def room_detail(self):
        return {
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'vacancy': self.vacancy,
            'deposit': self.deposit
        }


class RoomImage(BaseModel):
    """
    방의 이미지를 저장합니다.
    """
    __tablename__ = 'room_image'

    room_id = db.Column(db.Integer(), db.ForeignKey('housing_rooms.id'))
    url = db.Column(db.String(255))
    is_thumbnail = db.Column(db.Boolean, default=False)

    room = db.relationship('Room', backref=db.backref('images', lazy='dynamic'))

    def __repr__(self):
        return '<RoomImage %r>' % self.url


# 공동으로 쓰는 물건이나 시설을 정의함
class PublicFacilities(BaseModel):
    __tablename__ = 'housing_public_facilities'

    name = db.Column(db.String(100))
    description = db.Column(db.Text())
    image = db.Column(db.String(255))

    def __repr__(self):
        return '<PublicFacilities %r>' % self.name

    def get_public_facilities(self):
        return {
            'name': self.name,
            'description': self.description,
            'image': self.image
        }


# 각 방에 있는 물건이나 시설을 정의함
class PrivateFacilities(BaseModel):
    __tablename__ = 'housing_private_facilities'

    name = db.Column(db.String(100))
    description = db.Column(db.Text())
    image = db.Column(db.String(255))

    def __repr__(self):
        return '<PrivateFacilities %r>' % self.name

    def get_private_facilities(self):
        return {
            'name': self.name,
            'description': self.description,
            'image': self.image
        }


# confirm 받기 전에 예약 할 때 쓰는 테이블
class BookingStatus(BaseModel):
    __tablename__ = 'housing_booking_status'

    user_id = db.Column(db.Integer(), db.ForeignKey('auth_users.id'))
    housing_room_id = db.Column(db.Integer(), db.ForeignKey('housing_rooms.id'))
    is_confirmed = db.Column(db.Boolean(), default=False)
    bookeddate = db.Column(db.DateTime())
    bookeduserid = db.relationship('User', backref=db.backref('bookinstatus'))

    def __repr__(self):
        return '<BookingStatus %r>' % self.user_id

    def get_booking_status(self):
        return {
            'is_confirmed': self.is_confirmed,
            'bookeddate': self.bookeddate,
            'paid_date': self.paid_date,
            'housing_room_id': self.housing_room_id
        }


# 예약을 하고 confirm 이 떨어지면 이 테이블에 인서트 된다
class HousingPayment(BaseModel):
    __tablename__ = 'housing_payment'

    housing_booking_status_id = db.Column(db.Integer(), db.ForeignKey('housing_booking_status.id'))
    status = db.Column(db.Integer())
    price = db.Column(db.String(63))
    paid_date = db.Column(db.DateTime())
    user_id = db.Column(db.Integer(), db.ForeignKey('auth_users.id'))

    bookingstatusid = db.relationship('BookingStatus', backref=db.backref('housingpayment'))
    paiduserid = db.relationship('User', backref=db.backref('housingpayment'))

    def __repr__(self):
        return '<HousingPayment %r>' % self.housing_booking_status_id

    def get_housing_payment(self):
        return {
            'status': self.status,
            'price': self.price,
            'paid_date': self.paid_date,
            'user_id': self.user_id,
            'housing_booking_status_id': self.housing_booking_status_id
        }


# 숭실대학교 홍대 건대 종로3가 동대문 이태원 강남 ==> 6개의 main locations ~
class MainLocations(BaseModel):
    __tablename__ = 'housing_mainlocations'

    name = db.Column(db.String(55))
    realname = db.Column(db.String(55))
    address = db.Column(db.String(100))
    addressLat = db.Column(db.String(63))
    addressLong = db.Column(db.String(63))
    northeastLat = db.Column(db.DECIMAL(10, 6))
    northeastLng = db.Column(db.DECIMAL(10, 6))
    southwestLat = db.Column(db.DECIMAL(10, 6))
    southwestLng = db.Column(db.DECIMAL(10, 6))
    zoom = db.Column(db.Integer())
    image = db.Column(db.String(63))

    def __repr__(self):
        return '<MainLocations %r>' % self.name

    # 이런식으로 해도 되지만 query 문은 앞단에서 하기로 하고 아래에 있는 것 처럼 하기 !
    # @classmethod
    # def getmainlocationsnames(self):
    #     result = self.query.all()
    #     return result

    # 검색창 위에 띄울 메인로케이션들 !!
    def get_main_location(self):
        return {'name': self.name}

    def get_main_location_latlong(self):
        return {'name': self.name,
                'addressLat': self.addressLat,
                'addressLong': self.addressLong
                }


# 검색을 위한 테이블
class SearchLocations(BaseModel):
    __tablename__ = 'housing_searchlocations'

    name = db.Column(db.String(55))
    korean_name = db.Column(db.String(55))
    chinese_name = db.Column(db.String(55))
    addressLat = db.Column(db.DECIMAL(10, 6))
    addressLong = db.Column(db.DECIMAL(10, 6))
    northeastLat = db.Column(db.DECIMAL(10, 6))
    northeastLng = db.Column(db.DECIMAL(10, 6))
    southwestLat = db.Column(db.DECIMAL(10, 6))
    southwestLng = db.Column(db.DECIMAL(10, 6))

    def __repr__(self):
        return '<SearchLocations %r>' % self.name


# Housing service 예약 할 때 !
class Reservation(BaseModel):
    __tablename__ = 'housing_reservation'

    # 예약 하고자 하는 방 번호
    room_id = db.Column(db.Integer)

    # 로그인 되어 있는 아이디
    user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'), index=True)

    # (폼) 직접 받은  이름
    user_name = db.Column(db.String(55))

    # (폼) 직접 받은 이메일
    email = db.Column(db.String(55))

    # (폼) 직접 받은 카카오
    kakao_id = db.Column(db.String(55), nullable=True)

    # (폼) 직접 받은 핸드폰 번호
    mobile_no = db.Column(db.String(55), nullable=True)

    # (폼) 직접 받은 체크인 날짜
    checkin_date = db.Column(db.String(100))

    # (폼) 직접 받은 체크아웃 날짜
    checkout_date = db.Column(db.String(100))

    # (폼) 직접 받은 할말
    comments = db.Column(db.Text)

    # (폼) 어느나라에서 왔니
    nationality = db.Column(db.String(55))

    # 예약이 확인 되었는지 아닌지 확인
    """
    0: 예약 완료
    1: 예약 확인
    """
    reservation_status = db.Column(db.Integer, default=0)

    # 결제에 대한 관계키 설정 필요

    def __repr__(self):
        return '<Reservation %r>' % self.user_id

    def get_state(self):
        state = self.reservation_status
        if state == 0:
            return _("Reservation Applied")
        elif state == 1:
            return _("Reservation Successful ")


# 문의 하려고 남긴는 테이블
class Enquiry(BaseModel):
    __tablename__ = 'housing_enquiry'

    # 문의 하고자 하는 방 번호
    room_id = db.Column(db.Integer)

    # 로그인 되어 있는 아이디
    user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'), index=True)

    # (폼) 직접 받은  이름
    user_name = db.Column(db.String(55))

    # (폼) 직접 받은 이메일
    email = db.Column(db.String(55))

    # (폼) 직접 받은 카카오
    kakao_id = db.Column(db.String(55), nullable=True)

    # (폼) 직접 받은 핸드폰 번호
    mobile_no = db.Column(db.String(55), nullable=True)

    # (폼) 직접 받은 할말
    enquiry = db.Column(db.Text)

    # (폼) 어느나라에서 왔니
    nationality = db.Column(db.String(55))

    # 예약이 확인 되었는지 아닌지 확인
    """
    0: 문의 완료
    1: 답변 완료
    """
    enquiry_status = db.Column(db.Integer, default=0)

    # 결제에 대한 관계키 설정 필요

    def __repr__(self):
        return '<Enquiry %r>' % self.user_id

    def get_state(self):
        state = self.enquiry_status
        if state == 0:
            return _("Enquiry Applied")
        elif state == 1:
            return _("Enquiry Answered")
