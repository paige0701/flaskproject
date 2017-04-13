from flask import json
from flask_security import auth_token_required
from flask_restful import fields, Resource, marshal_with, reqparse, abort
from sqlalchemy.exc import IntegrityError

from apps import db
from apps.api_server import api
from .models import CatalogueCategory as _Category, CatalogueCategory, CatalogueCategoryDetail

# 1. Product 내용
# 2. Product 이미지
# 3. Product 디테일
# 4. Category별 프로덕트
# 5. Product 내용

product_resource = {
    'id': fields.Integer,
    'structure': fields.String,
    'upc': fields.String,
    'price': fields.Arbitrary(),
    'currency': fields.String(),
    'quantity': fields.Integer,

    'name': fields.String,
    'description': fields.String,
    'lang_code': fields.String
}


# # Look only in the POST body
# parser.add_argument('name', type=int, location='form')
#
# # Look only in the querystring
# parser.add_argument('PageSize', type=int, location='args')
#
# # From the request headers
# parser.add_argument('User-Agent', location='headers')
#
# # From http cookies
# parser.add_argument('session_id', location='cookies')
#
# # From file uploads
# parser.add_argument('picture', type=werkzeug.datastructures.FileStorage, location='files')

class CategoryAPI(Resource):
    # (parent code, depth)는 나중에 추가
    category_parser = reqparse.RequestParser()
    category_parser.add_argument('category_code', type=str, help='category_code will be 6 Character', required=True)
    category_parser.add_argument('name', type=str, required=True)
    category_parser.add_argument('description', type=str, required=True)
    category_parser.add_argument('lang_code', type=str, required=True)
    category_parser.add_argument('image', type=str)

    def get(self):
        return "A"
        pass

    def post(self):
        args = self.category_parser.parse_args()

        category_code = args.get('category_code')
        image = args.get('image')
        name = args.get('name')
        description = args.get('description')
        lang_code = args.get('lang_code')
        print(category_code)
        print(image)
        print(name)
        print(description)
        print(lang_code)

        category = CatalogueCategory.query.filter_by(category_code=category_code).first()
        print(category)
        if category is None:
            category = CatalogueCategory(category_code=category_code, image=image)
            db.session.add(category)
            print(category)

        category_detail = CatalogueCategoryDetail(name=name, description=description, lang_code=lang_code,
                                                  category_code=category)
        print(category_detail)
        try:
            db.session.add(category_detail)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(400, message='카테고리내 동일한 name값 사용 불가.')


        return category_detail, 201


api.add_resource(CategoryAPI, '/category')


class ProductAPI(Resource):
    def get(self):
        pass

    def post(self):
        CatalogueCategoryDetail
        category = CatalogueCategory(structure='', upc='', )
        pass


CategoryListAPI = {

}

product_image = {
    'is_thumbnail': fields.Boolean,
    'url': fields.String
}

product_list = {
    'id': fields.Integer,
    'name': fields.String,
    'upc': fields.String,
    'price': fields.String,
    'currency': fields.String,
    'quantity': fields.String,
    'description': fields.String,
    'image': fields.Nested(product_image, attribute='get_images')
    # 'thumbnail': fields.Url(),
}

product_list_fields_in_cgr = {
    'id': fields.Integer,
    'name': fields.String(attribute='name'),
    'products': fields.Nested(product_list, attribute='get_products')
}

categories_list = {
    'id': fields.Integer,
    'name': fields.String,
    'image': fields.String,
    'parent_id': fields.Integer,
    'depth': fields.Integer
}


class CategoryListAPI(Resource):
    """
    카테고리 리스트를 반환합니다.
    """

    @marshal_with(categories_list)
    def get(self):
        category = _Category.query.all()
        return category


class ProductListAPI(Resource):
    """
    해당 카테고리에 대한 제품 리스트를 반환합니다.
        :argument
            -page: 페이지 number
            -list: list 갯수 /1 page 당
    """

    # @auth_token_required
    @marshal_with(product_list_fields_in_cgr)
    def get(self, category_slug):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int)
        parser.add_argument('list', type=int)

        args = parser.parse_args()

        # args = parser.parse_args()
        page = args['page']
        list_size = args['list']
        if page is None:
            page = 0
        if list_size is None:
            list_size = 50

        category = _Category.query.filter_by(slug=category_slug).first()

        # products = category.get_product(page=page, list_size=list_size)

        # product_list_fields_in_cgr['products'] = products
        # marshal_with(fields.Nested(product_list, products))


        return category


api.add_resource(CategoryListAPI, '/categories')
api.add_resource(ProductListAPI, '/categories/<category_slug>')
