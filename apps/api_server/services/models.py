# from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
#
# from apps import db
# from apps.api_server.utils.abstract_models import BaseModel
#
#
# class ServiceType(BaseModel):
#     """
#     Service에 대한 Type 명시
#     """
#     __tablename__ = 'service_types'
#
#     name = db.Column(db.String(100))
#     description = db.Column(db.String(255))
#     can_delivery = db.Column(db.Boolean)
#
#     def __repr__(self):
#         return "<ServiceType %r>" % self.name
#
#
# class Service(BaseModel):
#     """
#     결제 가능한 모든 서비스를 넣는다.
#         upc: 서비스 고유 번호
#         type: 제품에 대한 type - 이름과 설명 delivery의 유무가 들어있다.
#         author: 작성자
#         partner: 연결된 파트너 (공급자)
#
#         slug: 해당 테이블이 참조할 테이블을 결정 (실제 제품).
#             ex) wirless first: w1로 표기
#             w: wireless
#                 1: secondHandWireless (중고 Wireless)
#                 2: prepaidSimCard (선불 심카드)
#                 3: chargeSimCard (심카드 충전)
#     """
#     __tablename__ = 'services'
#
#     upc = db.Column(db.String(100), unique=True)
#
#     type_id = db.Column(db.Integer, db.ForeignKey('service_types.id'))
#
#     slug = db.Column(db.String(6))
#
#     type = db.relationship('ServiceType', backref=db.backref('services', lazy='dynamic'),
#                            foreign_keys=[type_id])
#
#     author_user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'))
#     partner_id = db.Column(db.ForeignKey('auth_partners.id'))
#     author = db.relationship('User', backref=db.backref('posting_services', lazy='dynamic'),
#                              foreign_keys=[author_user_id])
#     partner = db.relationship('Partner', backref=db.backref('my_services', lazy='dynamic'),
#                               foreign_keys=[partner_id])
#
#     def __repr__(self):
#         return "<Service %r>" % self.upc
#
#     def get_slug(self):
#         return self.slug
#
#     def get_service(self):
#         result = {'slug': self.slug}
#
#         try:
#             if self.slug[0] == 'w':
#                 if self.slug[1] == '1':
#                     result['service'] = self.secondhand_wireless
#                 elif self.slug[1] == '2':
#                     result['service'] = self.prepaid_simcard
#         except:
#             result['service'] = None
#         finally:
#             return result
#
#
#     # user_가 가지고 있는 서비스 반환
#     @hybrid_property
#     def has_secondhand_wireless(self):
#         if self.secondhand_wireless:
#             return self.secondhand_wireless
#         else:
#             return None
