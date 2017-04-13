from flask.ext.admin.contrib.geoa import ModelView

from .custom_fields import CKTextAreaField


class MessageAdmin(ModelView):
    form_overrides = {
        'body': CKTextAreaField
    }
    create_template = 'ckeditor.html'
    edit_template = 'ckeditor.html'
