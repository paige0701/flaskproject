# category = CatalogueCategory.query.filter_by(category_code=category_code).first()
# print(category)
# if category is None:
#     category = CatalogueCategory(category_code=category_code, image=image)
#     db.session.add(category)
#     print(category)
#
# category_detail = CatalogueCategoryDetail(name=name, description=description, lang_code=lang_code,
#                                           category_code=category)
# print(category_detail)
# try:
#     db.session.add(category_detail)
#     db.session.commit()
# except IntegrityError:
#     db.session.rollback()
#     abort(400, message='카테고리내 동일한 name값 사용 불가.')
from flask_admin.form import FileUploadField, thumbgen_filename, namegen_filename, ImageUploadField, Select2Field
from flask_admin.contrib import sqla
from flask_security import current_user
from jinja2 import Markup
from wtforms import SelectField
from flask_s3 import url_for

from apps import db, app
from apps.api_server.services.catalogue_service.models import CatalogueCategoryDetail, CatalogueCategory, \
    CatalogueProduct, CatalogueProductDetail, CatalogueProudctImage
from apps.dashboards import admin
from apps.dashboards.utils.custom_fields import CloudFileUploadField, CloudImageUploadField
from apps.utils.file_manager import url_for_s3

media_path = app.config['MEDIA_PATH']
PRODUCT_STRUCTURE_CHOICES = app.config['PRODUCT_STRUCTURE_CHOICES'].copy()
IMAGE_ALLOWED_EXTENSIONS = ('gif', 'jpg', 'jpeg', 'png', 'tiff')




class CatalogueAdminView(sqla.ModelView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if 'superuser' in current_user.roles or 'staff' in current_user.roles:
            return True

        return False

    can_create = True
    can_edit = True
    can_delete = True
    column_display_pk = True
    can_export = True
    can_view_details = True
    # column action!!
    # https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView.column_extra_row_actions
    # column_extra_row_actions = [
    #     LinkRowAction('glyphicon glyphicon-off', 'http://direct.link/?id={row_id}'),
    #     EndpointLinkRowAction('glyphicon glyphicon-test', 'admin.index')
    # ]
    create_modal = True
    # create_modal_template = 'admin/model/modals/create.html'
    edit_modal = True
    # A list of available export filetypes. csv only is default, but any filetypes supported by tablib can be used.
    # Check tablib for https: //github.com / kennethreitz / tablib / blob / master / README.rst for supported types.
    # list에서 편집 가능하게 하는 columns
    # column_editable_list = ( 'confirmed_at', 'country')
    details_modal = True


class CategoryView(CatalogueAdminView):
    column_list = (
        'category_code', 'categories', 'get_category_lang', 'get_need_lang', 'image', 'created_at', 'is_display')

    form_columns = ('category_code', 'categories', 'image', 'is_display')
    inline_models = [(CatalogueCategoryDetail,
                      dict(form_columns=['id', 'name', 'description', 'lang_code'],
                           form_extra_fields={'lang_code': SelectField('Language', choices=[
                               (key, app.config['LANG_CHOICES'][key]) for key in
                               app.config['LANG_CHOICES']])
                                              }
                           ))]

    # : FileUploadField field requires base_path to be set.
    form_overrides = dict(image=CloudImageUploadField)

    form_args = dict(
            image={
                'label': 'Category Image',
                'storage_type': 's3',
                'allowed_extensions': IMAGE_ALLOWED_EXTENSIONS,
                'allow_overwrite': False,
                # 자르기 사이즈
                'thumbnail_size': (100, 100, True),
                'endpoint': 'media',
                'relative_path':'category/',
                # 'relative_path':'category',
                'url_relative_path': 'category',
                'base_path': 'media',
            },
    )

    column_labels = {
        'get_need_lang': 'need_lang',
        'get_category_lang': 'language',
    }

    # 빼내기 ( product에서 쓸듯)
    def _list_thumbnail(view, context, model, name):
        if not model.image:
            return ''

        # file 가져오기 (thumb 적혀있음)

        # return Markup('<img src="%s">' % url_for('media', filename=thumbgen_filename(model.image)))
        return Markup('<img src="%s">' % url_for_s3('media', filename=thumbgen_filename(model.image)))
        # return Markup('<img src="%s">' % url_for('media', filename=namegen_filename()))

    # column format
    column_formatters = {
        'image': _list_thumbnail
    }

    # column_searchable_list = ('category_code.category_code', 'name', 'lang_code')
    column_searchable_list = ('categories.name', 'categories.lang_code', 'category_code')

    # form extra fields
    # form_extra_fields = {
    #     'lang_code': SelectField('Language',
    #                              choices=[(key, app.config['LANG_CHOICES'][key]) for key in app.config['LANG_CHOICES']]),
    #     'image': FileUploadField('Image',
    #                              base_path=media_path,)
    # }


    # form_ajax_refs = {
    #     'roles': {
    #         'fields': ('name', 'description'),
    #         'page_size': 10
    #     }
    # }
    # excel로 export
    column_details_list = ('category_code', 'categories', 'get_category_lang', 'image', 'created_at',)
    column_export_list = ('category_code', 'categories', 'get_category_lang', 'image', 'created_at',)


class ProductView(CatalogueAdminView):
    column_list = (
        'upc', 'price', 'currency', 'quantity', 'structure', 'get_thumbnail_image', 'get_product_lang', 'get_need_lang',
        'type', 'category', 'created_at',)

    # column_list = ('category_code', 'categories', 'get_category_lang', 'get_need_lang', 'image', 'created_at',)

    form_columns = ('upc', 'price', 'currency', 'quantity', 'structure', 'images', 'product_detail', 'type', 'category')
    form_overrides = dict(structure=Select2Field)
    form_extra_fields = {
        'structure': Select2Field('Structure',
                                  choices=[(key, PRODUCT_STRUCTURE_CHOICES[key]) for key in PRODUCT_STRUCTURE_CHOICES])
    }

    # 빼내기 ( product에서 쓸듯)
    def _list_thumbnail(view, context, model, name):
        if not model.get_thumbnail_image:
            return ''

        # file 가져오기 (thumb 적혀있음)

        # return Markup('<img src="%s">' % url_for('media', filename=thumbgen_filename(model.image)))
        return Markup('<img src="%s">' % url_for_s3('media', filename=thumbgen_filename(model.get_thumbnail_image)))
        # return Markup('<img src="%s">' % url_for('media', filename=namegen_filename()))

    # column format
    column_formatters = {
        'get_thumbnail_image': _list_thumbnail
    }

    column_labels = {
        'get_thumbnail_image': 'primary image',
        'get_product_lang': 'language',
    }

    inline_models = [(CatalogueProductDetail,
                      dict(form_columns=['id', 'name', 'description', 'lang_code'],
                           form_extra_fields={'lang_code': SelectField('Language', choices=[
                               (key, app.config['LANG_CHOICES'][key]) for key in app.config['LANG_CHOICES']
                               ])})),
                     (CatalogueProudctImage,
                      dict(form_columns=['id', 'url', 'is_thumbnail'],
                           form_extra_fields={'url': CloudImageUploadField('Product Image',
                                                                           storage_type= 's3',
                                                                           allowed_extensions= IMAGE_ALLOWED_EXTENSIONS,
                                                                           allow_overwrite=False,
                                                                           base_path='media',
                                                                           thumbnail_size=(300, 300, True),
                                                                           endpoint='media',
                                                                           relative_path="products/",
                                                                           url_relative_path='products'), })
                      ), ]



    column_details_list = ('category_code', 'categories', 'get_category_lang', 'image', 'created_at',)
    column_export_list = ('category_code', 'categories', 'get_category_lang', 'image', 'created_at',)


class TypeView(CatalogueAdminView):
    pass


admin.add_view(CategoryView(CatalogueCategory, db.session, category="Catalogue"))
admin.add_view(ProductView(CatalogueProduct, db.session, category="Catalogue"))
