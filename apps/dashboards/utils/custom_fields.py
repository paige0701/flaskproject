import os
from urllib.parse import urljoin

import boto3
import re

try:
    from PIL import Image, ImageOps
except ImportError:
    Image = None
    ImageOps = None

from flask import current_app
from flask_babel import gettext
from flask_admin.form import ImageUploadField, ImageUploadInput, FileUploadField
# from six import BytesIO
from io import BytesIO
from wtforms import TextAreaField, ValidationError
from wtforms.widgets import TextArea

from apps.utils.file_manager import url_for_s3


class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()


# ------------------- 구분선 ----------------------

ENABLE_S3_STORAGE_TYPE = ['s3', ]
ENABLE_S3_REGION_NAME = ['ap-northeast-2', ]
IMAGE_ALLOWED_EXTENSIONS = ('gif', 'jpg', 'jpeg', 'png', 'tiff', 'pdf')


class CloudFileUploadField(FileUploadField):
    """
    Inherits from flask-admin FileUploadField, to allow file uploading
    to Cloud (S3, Azure ...)
    """

    def __init__(self, label=None, validators=None, namegen=None, allowed_extensions=None, allow_overwrite=True,
                 storage_type=None, region_name=None, bucket_name=None, access_key_id=None, access_key_secret=None,
                 acl='public-read', bucket_root=None, relative_path=None, **kwargs):
        super(CloudFileUploadField, self).__init__(label, validators, namegen=namegen, allow_overwrite=allow_overwrite,
                                                   allowed_extensions=allowed_extensions, **kwargs)

        if storage_type not in ENABLE_S3_STORAGE_TYPE:
            raise ValueError(
                    'Storage type "%s" is invalid, the only supported storage type'
                    ' (apart from default local storage) is %s.' % (storage_type, ENABLE_S3_STORAGE_TYPE)
            )

        self.storage_type = storage_type
        self.bucket_name = bucket_name or current_app.config['FLASKS3_MEDIA_BUCKET_NAME']
        self.access_key_id = access_key_id or current_app.config['AWS_ACCESS_KEY_ID']
        self.access_key_secret = access_key_secret or current_app.config['AWS_SECRET_ACCESS_KEY']
        self.acl = acl
        self.region_name = region_name or current_app.config['FLASKS3_REGION']
        self.bucket_root = bucket_root or current_app.config['FLASKS3_MEDIA_BUCKET_ROOT']
        self.relative_path = relative_path

    def populate_obj(self, obj, name):
        field = getattr(obj, name, None)
        if field:
            # If field should be deleted, clean it up
            if self._should_delete:
                self._delete_file(field, obj)
                setattr(obj, name, '')
                return

        if self._is_uploaded_file(self.data):
            if field:
                self._delete_file(field, obj)

            filename = self.generate_name(obj, self.data)
            filename = self._save_file(self.data, filename)
            # update filename of FileStorage to our validated name
            self.data.filename = filename

            setattr(obj, name, filename)

    def generate_name(self, obj, file_data):
        filename = super(CloudFileUploadField, self).generate_name(obj, self.data)
        if self.storage_type is 's3':
            filename = urljoin(self.base_path, filename)
        print('gen', filename)
        return filename

    def pre_validate(self, form):
        """
        검사
        """
        if self._is_uploaded_file(self.data) and not self.is_file_allowed(self.data.filename):
            raise ValidationError(gettext('Invalid file extension'))

        # Handle overwriting existing content
        if not self._is_uploaded_file(self.data):
            return

            # 수정 필요. 존재하는지 확인
            # if not self._allow_overwrite and os.path.exists(self._get_path(self.data.filename)):
            #     raise ValidationError(gettext('File "%s" already exists.' % self.data.filename))

    def _save_file(self, data, filename):
        if self.storage_type not in ENABLE_S3_STORAGE_TYPE:
            raise ValueError(
                    'Storage type "%s" is invalid, the only supported storage type'
                    ' (apart from default local storage) is %s.' % (self.storage_type, ENABLE_S3_STORAGE_TYPE)
            )

        if self.storage_type is 's3':
            # filename = os.path.join(self.bucket_root, self.relative_path, filename)
            file = self._save_file_s3(data, filename)
        else:
            file = None

        print('save', filename)
        return file

    def _save_file_s3(self, data, filename):
        if self.storage_type is not 's3':
            raise ValueError(
                    'Storage type %s is invalid, the only supported storage type is s3' % self.storage_type
            )
        if not self.access_key_id and not self.access_key_secret:
            raise ValueError('Storage type s3 have to access_key id, access_key_secret')

        s3_resource = boto3.resource('s3',
                                     self.region_name,
                                     # Hard coded strings as credentials, not recommended.
                                     aws_access_key_id=self.access_key_id,
                                     aws_secret_access_key=self.access_key_secret)

        bucket = s3_resource.Bucket(self.bucket_name)
        print('hoho', data)
        filename = os.path.join(self.bucket_root, filename)
        data.seek(0)
        bucket.upload_fileobj(data, filename, ExtraArgs={'ACL': 'public-read'})

        return filename

    def _delete_file(self, filename, obj):
        if self.storage_type not in ENABLE_S3_STORAGE_TYPE:
            raise ValueError(
                    'Storage type "%s" is invalid, the only supported storage type'
                    ' (apart from default local storage) is %s.' % (self.storage_type, ENABLE_S3_STORAGE_TYPE)
            )

        if self.storage_type is 's3':
            delete_response = self._delete_file_s3(filename, obj)
        else:
            delete_response = None
        return delete_response

    def _get_s3_path(self, filename):
        if not self.bucket_root:
            raise ValueError('S3FileUploadField field requires ''bucket_root to be set.')
        return os.path.join(self.bucket_root, self.relative_path, filename)

    def _delete_file_s3(self, filename, obj):
        if self.storage_type is not 's3':
            raise ValueError(
                    'Storage type %s is invalid, the only supported storage type is s3' % self.storage_type
            )
        if not self.access_key_id and not self.access_key_secret:
            raise ValueError('Storage type s3 have to access_key id, access_key_secret')

        s3_resource = boto3.resource('s3',
                                     self.region_name,
                                     # Hard coded strings as credentials, not recommended.
                                     aws_access_key_id=self.access_key_id,
                                     aws_secret_access_key=self.access_key_secret)

        bucket = s3_resource.Bucket(self.bucket_name)

        response = bucket.delete_objects(
                Delete={
                    'Objects': [
                        {
                            'Key': filename,

                        }
                    ]
                }
        )
        return response


class CloudImageUploadInput(ImageUploadInput):
    """
    Inherits from flask-admin ImageUploadInput, to render images
    uploaded to Amazon S3 (as well as the default local storage).
    """

    def get_url(self, field):
        if os.path.isfile(os.path.join(field.base_path, field.data)):
            return super(CloudImageUploadInput, self).get_url(field)

        if field.thumbnail_size:
            filename = field.thumbnail_fn(field.data)
        else:
            filename = field.data

        if field.url_relative_path:
            filename = urljoin(field.url_relative_path, filename)

        return url_for_s3(field.endpoint, bucket_name=field.bucket_name,
                          filename=filename)


class CloudImageUploadField(CloudFileUploadField):
    """
        Cloud Image upload field.

        Does image validation, thumbnail generation, updating and deleting images.

        Requires PIL (or Pillow) to be installed.
    """
    widget = CloudImageUploadInput()
    keep_image_formats = ('PNG',)

    def __init__(self, label=None, validators=None, namegen=None, allowed_extensions=None, allow_overwrite=True,
                 storage_type=None, region_name=None, bucket_name=None, access_key_id=None, access_key_secret=None,
                 acl='public-read', bucket_root=None, relative_path=None, max_size=None, thumbgen=None,
                 thumbnail_size=None, url_relative_path=None, endpoint=None, **kwargs):
        if Image is None:
            raise ImportError('PIL library was not found')

        self.max_size = max_size
        self.thumbnail_fn = thumbgen or thumbgen_filename
        self.thumbnail_size = thumbnail_size
        self.endpoint = endpoint
        self.image = None
        self.url_relative_path = url_relative_path

        if allowed_extensions is None:
            allowed_extensions = IMAGE_ALLOWED_EXTENSIONS

        super(CloudImageUploadField, self).__init__(label, validators, namegen, allowed_extensions, allow_overwrite,
                                                    storage_type, region_name,
                                                    bucket_name, access_key_id, access_key_secret, acl, bucket_root,
                                                    relative_path, **kwargs)

    def pre_validate(self, form):
        super(CloudImageUploadField, self).pre_validate(form)

        if self._is_uploaded_file(self.data):
            try:
                self.image = Image.open(self.data)
            except Exception as e:
                raise ValidationError("Invalid image: %s" % e)

    def _delete_file(self, filename, obj):
        super(CloudImageUploadField, self)._delete_file(filename, obj)

        self._delete_thumbnail(filename, obj)

    def _delete_thumbnail(self, filename, obj):
        """
        썸네일 삭제
        :param filename:
        :param obj:
        :return:
        """
        if self.storage_type is 's3':
            self._delete_thumbnail_s3(filename, obj)

    def _delete_thumbnail_s3(self, filename, obj):
        """
        s3 썸네일 삭제
        :param filename:
        :param obj:
        :return:
        """
        return super(CloudImageUploadField, self)._delete_file_s3(self.thumbnail_fn(filename), obj)

    def _save_file(self, data, filename):

        if self.storage_type not in ENABLE_S3_STORAGE_TYPE:
            raise ValueError(
                    'Storage type "%s" is invalid, the only supported storage type'
                    ' (apart from default local storage) is %s.' % (self.storage_type, ENABLE_S3_STORAGE_TYPE))

        # Figure out format
        filename, format = self._get_save_format(filename, self.image)
        print(self.image)
        if self.image:  # and (self.image.format != format or self.max_size):
            if self.max_size:
                image = self._resize(self.image, self.max_size)
            else:
                image = self.image

            temp_file = BytesIO()
            self._save_image(image, temp_file, format)
            print(temp_file.getvalue())
            temp_file.seek(0)
            print(temp_file.getvalue())

        super(CloudImageUploadField, self)._save_file(temp_file, filename)

        thumbnail_data = BytesIO()

        self._save_thumbnail(thumbnail_data, filename, format)
        return filename

    def _save_thumbnail(self, data, filename, format):
        if self.image and self.thumbnail_size:
            self._save_image(self._resize(self.image, self.thumbnail_size), data, format)
            print('save_thumbnail')

            super(CloudImageUploadField, self)._save_file(data, self.thumbnail_fn(filename))

    def _resize(self, image, size):
        (width, height, force) = size

        if image.size[0] > width or image.size[1] > height:
            if force:
                return ImageOps.fit(self.image, (width, height), Image.ANTIALIAS)
            else:
                thumb = self.image.copy()
                thumb.thumbnail((width, height), Image.ANTIALIAS)
                return thumb

        return image

    def _save_image(self, image, temp_file, format='JPEG'):
        if image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGBA')

        image.save(temp_file, format)

    def _get_save_format(self, filename, image):
        if image.format not in self.keep_image_formats:
            name, ext = os.path.splitext(filename)
            filename = '%s.jpg' % name
            return filename, 'JPEG'

        return filename, image.format


def thumbgen_filename(filename):
    """
        Generate thumbnail name from filename.
    """
    name, ext = os.path.splitext(filename)
    return '%s_thumb%s' % (name, ext)
