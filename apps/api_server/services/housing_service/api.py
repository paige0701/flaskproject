from flask_restful import fields, Resource, marshal_with

housinglist_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'address1': fields.String,
    'address2': fields.String,
    'description': fields.String,
    'latitude': fields.Float,
    'longitude': fields.Float,
    'lowest_price': fields.String(attribute='get_lowest_price'),

    # 'price': fields.Nested(nested='',attribute=)
}
#
# class Marker(Resource):
#     @marshal_with(housinglist_fields, envelope="result")
#     def get(self):
#         # print("dddd")
#         # print(request.environ)
#         # for env in request.environ:
#         #     print(env, ": ", request.environ[env])
#         # print(request.args)
#         sw_x = request.args.get('sw_x')
#         sw_y = request.args.get('sw_y')
#         ne_x = request.args.get('ne_x')
#         ne_y = request.args.get('ne_y')
#
#
#         print(sw_x)
#         print(sw_y)
#         print(ne_x)
#         print(ne_y)
#         if not (sw_x and sw_y and ne_x and ne_y):
#             housing = Housing.query.all()
#         else:
#             housing = Housing.query.filter(Housing.latitude > sw_x, Housing.latitude < ne_x,
#                                            Housing.longitude > sw_y, Housing.longitude < ne_y).order_by(Housing.name).all()
#
#
#         print(housing)
#
#         return housing
#
#
# api.add_resource(Marker, '/marker')
