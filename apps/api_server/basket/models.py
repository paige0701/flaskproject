# from apps import db
# from apps.api_server.utils.abstract_models import BaseModel
#
#
# # 'basket'과 'services'라인과의 다대다 테이블
# baskets_services_line = db.Table('baskets_services_line',
#                                  db.Column('id', db.Integer,primary_key=True),
#                                  db.Column('basket_id', db.Integer, db.ForeignKey('baskets.id')),
#                                  db.Column('services_id', db.Integer, db.ForeignKey('services.id')),
#                                  db.Column('quantity', db.Integer))
#
#
# class Basket(BaseModel):
#     """
#     Basket 테이블
#     """
#     __tablename__ = 'baskets'
#
#     user_id = db.Column(db.Integer(), db.ForeignKey('auth_users.id'))
#     # state must be Integer (0: thaw, 1: frozen, 2: complete)
#     state = db.Column(db.Integer)
#
#     # Basket 소유주
#     master = db.relationship('User', backref= db.backref('baskets',lazy='dynamic'))
#     # service line 에 대한 정보
#     lines = db.relationship('Service', secondary=baskets_services_line)
#
#     def get_lines(self):
#         # list 형태로 line을 반환함
#         return self.lines
#
#     def get_master(self):
#         return self.master
#
#     def __repr__(self):
#         return "<Basket %r>" % self.id
#
#
#
#
#
