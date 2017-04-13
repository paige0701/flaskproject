import os
import errno
from io import BytesIO

import boto3
import botocore

try:
    from PIL import Image, ImageOps
except ImportError:
    raise RuntimeError('Image module of PIL needs to be installed')


class Thumbnail(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        self.app = app
        self.media_type = app.config.get('MEDIA_TYPE', None)
        self.media_bucket_name = app.config.get('MEDIA_BUCKET_NAME', None)

        self.media_root = app.config.get('MEDIA_ROOT', 'media')
        self.media_thumbnail_root = app.config.get('THUMBNAIL_ROOT', 'thumbnail')

        aws_access_key_id = app.config.get('AWS_ACCESS_KEY_ID', None)
        aws_access_key_secret = app.config.get('AWS_SECRET_ACCESS_KEY', None)
        self.aws_region = app.config.get('MEDIA_REGION', None)

        if self.media_type is None:
            raise RuntimeError(
                    'You\'re using the flask-thumbnail app without having set the required MEDIA_FOLDER setting.')

        if aws_access_key_id is None or aws_access_key_secret is None:
            raise RuntimeError('You need to AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY')

        if self.media_bucket_name is None:
            raise RuntimeError('You have to setting "Media Bucket Name "')

        self.bucket = boto3.resource('s3',
                                     self.aws_region,
                                     aws_access_key_id=aws_access_key_id,
                                     aws_secret_access_key=aws_access_key_secret).Bucket(self.media_bucket_name)

        app.jinja_env.filters['thumbnail'] = self.thumbnail

    def thumbnail(self, img_url, size, crop=None, bg=None, quality=85):
        width, height = [int(x) for x in size.split('x')]
        url_path, img_name = os.path.split(img_url)

        name, fe = os.path.splitext(img_name)

        thumbnail_name = self._get_name(name, fe, size, crop, bg, quality)

        original_filename = os.path.join(self.media_root, img_url)
        thumb_filename = os.path.join(self.media_thumbnail_root, url_path, thumbnail_name)

        if self.is_file_exist(thumb_filename):
            file_url = self.get_file_url(thumb_filename)
        elif self.is_file_exist(original_filename):
            thumb_size = (width, height)
            try:
                file = self.bucket.Object(original_filename).get()
                original_image = Image.open(file['Body'])

            except IOError:
                return None
            if crop == 'fit':
                thumb_img = ImageOps.fit(original_image, thumb_size, Image.ANTIALIAS)
            else:
                thumb_img = original_image.copy()
                thumb_img.thumbnail((width, height), Image.ANTIALIAS)
            if bg:
                thumb_img = self._bg_square(thumb_img, bg)
            # 임시파일 저장
            temp_file = BytesIO()
            self._save_image(thumb_img, temp_file)
            temp_file.seek(0)
            self.upload_image(temp_file,thumb_filename)

            file_url = self.get_file_url(thumb_filename)

        else:
            file_url = self.get_file_url('media/not_found.jpg')

        return file_url

    @staticmethod
    def _bg_square(img, color=0xff):
        size = (max(img.size),) * 2
        layer = Image.new('L', size, color)
        layer.paste(img, tuple(map(lambda x: (x[0] - x[1]) / 2, zip(size, img.size))))
        return layer

    @staticmethod
    def _get_name(name, fe, *args):
        """
        :param name: original_name
        :param fe: file_extension
        :param args: file thumbnail attribute
        """
        for v in args:
            if v:
                name += '_%s' % v
        name += fe

        return name

    def is_file_exist(self, filename):
        exists = False
        try:
            self.bucket.Object(filename).load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                exists = False
            else:
                raise
        else:
            exists = True

        return exists

    def get_file_url(self, filename, scheme='https', url_style='host', bucket_domain=None, cdn_domain=None):

        if url_style == 'host':
            url_format = '%(bucket_name)s.%(bucket_domain)s'
        elif url_style == 'path':
            url_format = '%(bucket_domain)s/%(bucket_name)s'
        else:
            raise ValueError('Invalid S3 URL Style: "%s"')

        if bucket_domain is None:
            bucket_domain = 's3.amazonaws.com'
            bucket_path = url_format % {
                'bucket_name': self.media_bucket_name,
                'bucket_domain': bucket_domain,
            }

        if cdn_domain:
            bucket_path = "%s" % cdn_domain

        return str("%s//%s/%s" % (
            scheme + (':' if scheme else ''),
            bucket_path,
            filename.lstrip('/')
        ))

    def upload_image(self, image, filename):
        print(image)
        # re = self.bucket.upload_fileobj(image, filename, ExtraArgs={'ACL': 'public-read'})
        # print(re)
        self.bucket.upload_fileobj(image, filename, ExtraArgs={'ACL': 'public-read'})
        # try:
        #     self.bucket.upload_fileobj(image, filename, ExtraArgs={'ACL': 'public-read'})
        #     print('ss')
        # except:
        #     print('kk')
        #     return None
        print('ik')
        return True

    def _save_image(self, image, temp_file, format='JPEG'):
        if image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGBA')

        image.save(temp_file, format)










        # self.thumbnail_url

# # 오리지날 이미지:
#         # bucket: media_files
#         # root_folder: media
#         # 원본 file_path: db에 저장된 path


# import os
# import errno
#
# try:
#     from PIL import Image, ImageOps
# except ImportError:
#     raise RuntimeError('Image module of PIL needs to be installed')
#
#
# class Thumbnail(object):
#     def __init__(self, app=None):
#         if app is not None:
#             self.init_app(app)
#         else:
#             self.app = None
#
#     def init_app(self, app):
#         """
#         :param app:
#         :key  config media_type: means media_type (s3, local)
#         :key thumbnail_folder: means thumbnail folder for saving thumbnail image
#         :key thumbnail_url: means url that is acceptable image files
#         """
#         self.app = app
#         self.media_type = self.app.config.get('MEDIA_TYPE', None)
#         self.thumbnail_folder = self.app.config.get('MEDIA_THUMBNAIL_FOLDER', None)
#         self.thumbnail_url = self.app.config.get('MEDIA_THUMBNAIL_URL', None)
#
#         if not self.media_type:
#             raise RuntimeError('You\'re using the flask-thumbnail app '
#                                'without having set the required MEDIA_FOLDER setting.')
#         if not self.thumbnail_folder:
#             raise RuntimeError('You\'re set MEDIA_THUMBNAIL_FOLDER setting. for saving thumbnail_image')
#
#         if not self.thumbnail_url:
#             raise RuntimeError('You\'re set and MEDIA_THUMBNAIL_URL setting. It is for that acceptable Image files URL')
#
#         app.jinja_env.filters['thumbnail'] = self.thumbnail
#
#
#     def thumbnail(self, img_url, size, crop=None, bg=None, quality=85):
#         """
#
#         :param img_url: url img - '/assets/media/summer.jpg'
#         :param size: size return thumb - '100x100'
#         :param crop: crop return thumb - 'fit' or None
#         :param bg: tuple color or None - (255, 255, 255, 0)
#         :param quality: JPEG quality 1-100
#         :return: thumb_url
#         """
#         # size 받아오기
#         width, height = [int(x) for x in size.split('x')]
#
#         # url에서 디렉토리와 파일이름 가져오기
#         url_path, img_name = os.path.split(img_url)
#
#         # 파일이름에서 이름과 확장자 분리하기
#         name, fm = os.path.splitext(img_name)
#
#         # 썸네일 이름 가져오기 (생성) -확장자 그대로
#         miniature = self._get_name(name, fm, size, crop, bg, quality)
#
#         # 원본 파일이름 가져오기
#         original_filename = os.path.join(self.app.config['MEDIA_FOLDER'], url_path, img_name)
#
#         # if self.media_type is 's3':
#         #     return self.s3_thumbnail(img_url, size, crop, bg, quality)
#
#         # 썸네일 파일 path가져오기
#         thumb_filename = os.path.join(self.app.config['MEDIA_THUMBNAIL_FOLDER'], url_path, miniature)
#
#         # create folders 및 file path만들기
#         self._get_path(thumb_filename)
#
#         thumb_url = os.path.join(self.app.config['MEDIA_THUMBNAIL_URL'], url_path, miniature)
#
#         if os.path.exists(thumb_filename):
#             return thumb_url
#
#         elif not os.path.exists(thumb_filename):
#             thumb_size = (width, height)
#             try:
#                 image = Image.open(original_filename)
#             except IOError:
#                 return None
#
#             if crop == 'fit':
#                 img = ImageOps.fit(image, thumb_size, Image.ANTIALIAS)
#             else:
#                 img = image.copy()
#                 img.thumbnail((width, height), Image.ANTIALIAS)
#
#             if bg:
#                 img = self._bg_square(img, bg)
#
#             img.save(thumb_filename, image.format, quality=quality)
#
#             return thumb_url
#
#     def s3_thumbnail(self, img_url, size, crop=None, bg=None, quality=85):
#         # 오리지날 이미지:
#         # bucket: media_files
#         # root_folder: media
#         # 원본 file_path: db에 저장된 path
#         width, height = [int(x) for x in size.split('x')]
#
#         # url에서 디렉토리와 파일이름 가져오기
#         url_path, img_name = os.path.split(img_url)
#
#         # 파일이름에서 이름과 확장자 분리하기
#         name, fm = os.path.splitext(img_name)
#
#         # 썸네일 이름 가져오기 (생성) -확장자 그대로
#         miniature = self._get_name(name, fm, size, crop, bg, quality)
#
#         # 원본 파일이름 가져오기
#         original_filename = os.path.join(self.app.config['MEDIA_FOLDER'], url_path, img_name)
#
#
#
#
#         # 1. 썸네일 있는지 확인
#         # 2. 없으면 원본 있는지 확인
#         # 3. 없으면 생성
#         # 4. return thumb_url
#         pass
#
#     @staticmethod
#     def _bg_square(img, color=0xff):
#         """
#         set the background layer
#         :param img:
#         :param color:
#         :return:
#         """
#         size = (max(img.size),) * 2
#         layer = Image.new('L', size, color)
#         layer.paste(img, tuple(map(lambda x: (x[0] - x[1]) / 2, zip(size, img.size))))
#         return layer
#
#     @staticmethod
#     def _get_path(full_path):
#         directory = os.path.dirname(full_path)
#
#         try:
#             if not os.path.exists(full_path):
#                 os.makedirs(directory)
#         except OSError as e:
#             if e.errno != errno.EEXIST:
#                 raise
#
#     @staticmethod
#     def _get_name(name, fm, *args):
#         for v in args:
#             if v:
#                 name += '_%s' % v
#         name += fm
#
#         return name
#
#
#
#
#
#         # aws에 있는지 확인
#         # 있으면 return
#         # 없으면 원본 가져온 후 생성후 return
#
#
# def thumbnail(self, img_url, size, crop=None, bg=None, quality=85):
#     """
#     :param img_url: url img - '/assets/media/summer.jpg'
#     :param size: size return thumb - '100x100'
#     :param crop: crop return thumb - 'fit' or None
#     :param bg: tuple color or None - (255, 255, 255, 0)
#     :param quality: JPEG quality 1-100
#     :return: :thumb_url:
#     """
#     width, height = [int(x) for x in size.split('x')]
#     url_path, img_name = os.path.split(img_url)
#     name, fm = os.path.splitext(img_name)
#
#     miniature = self._get_name(name, fm, size, crop, bg, quality)
#
#     original_filename = os.path.join(self.app.config['MEDIA_FOLDER'], url_path, img_name)
#     thumb_filename = os.path.join(self.app.config['MEDIA_THUMBNAIL_FOLDER'], url_path, miniature)
#
#     # create folders
#     self._get_path(thumb_filename)
#
#     thumb_url = os.path.join(self.app.config['MEDIA_THUMBNAIL_URL'], url_path, miniature)
#
#     if os.path.exists(thumb_filename):
#         return thumb_url
#
#     elif not os.path.exists(thumb_filename):
#         thumb_size = (width, height)
#         try:
#             image = Image.open(original_filename)
#         except IOError:
#             return None
#
#         if crop == 'fit':
#             img = ImageOps.fit(image, thumb_size, Image.ANTIALIAS)
#         else:
#             img = image.copy()
#             img.thumbnail((width, height), Image.ANTIALIAS)
#
#         if bg:
#             img = self._bg_square(img, bg)
#
#         img.save(thumb_filename, image.format, quality=quality)
#
#         return thumb_url
#
#     def thumbnail(self, img_url, size, crop=None, bg=None, quality=85):
#         """
#
#         :param img_url: url img - '/assets/media/summer.jpg'
#         :param size: size return thumb - '100x100'
#         :param crop: crop return thumb - 'fit' or None
#         :param bg: tuple color or None - (255, 255, 255, 0)
#         :param quality: JPEG quality 1-100
#         :return: :thumb_url:
#         """
#         width, height = [int(x) for x in size.split('x')]
#         url_path, img_name = os.path.split(img_url)
#         name, fm = os.path.splitext(img_name)
#
#         miniature = self._get_name()
#
#
# class Thumbnail(object):
#     def __init__(self, app=None):
#         if app is not None:
#             self.app = app
#             self.init_app(self.app)
#         else:
#             self.app = None
#
#     def init_app(self, app):
#         self.app = app
#
#         if not self.app.config.get('MEDIA_FOLDER', None):
#             raise RuntimeError('You\'re using the flask-thumbnail app '
#                                'without having set the required MEDIA_FOLDER setting.')
#
#         if self.app.config.get('MEDIA_THUMBNAIL_FOLDER', None) and not self.app.config.get('MEDIA_THUMBNAIL_URL', None):
#             raise RuntimeError('You\'re set MEDIA_THUMBNAIL_FOLDER setting, need set and MEDIA_THUMBNAIL_URL setting.')
#
#         app.config.setdefault('MEDIA_THUMBNAIL_FOLDER', os.path.join(self.app.config['MEDIA_FOLDER'], ''))
#         app.config.setdefault('MEDIA_URL', '/')
#         app.config.setdefault('MEDIA_THUMBNAIL_URL', os.path.join(self.app.config['MEDIA_URL'], ''))
#
#         app.jinja_env.filters['thumbnail'] = self.thumbnail
#
#     def thumbnail(self, img_url, size, crop=None, bg=None, quality=85):
#         """
#         :param img_url: url img - '/assets/media/summer.jpg'
#         :param size: size return thumb - '100x100'
#         :param crop: crop return thumb - 'fit' or None
#         :param bg: tuple color or None - (255, 255, 255, 0)
#         :param quality: JPEG quality 1-100
#         :return: :thumb_url:
#         """
#         width, height = [int(x) for x in size.split('x')]
#         url_path, img_name = os.path.split(img_url)
#         name, fm = os.path.splitext(img_name)
#
#         miniature = self._get_name(name, fm, size, crop, bg, quality)
#
#         original_filename = os.path.join(self.app.config['MEDIA_FOLDER'], url_path, img_name)
#         thumb_filename = os.path.join(self.app.config['MEDIA_THUMBNAIL_FOLDER'], url_path, miniature)
#
#         # create folders
#         self._get_path(thumb_filename)
#
#         thumb_url = os.path.join(self.app.config['MEDIA_THUMBNAIL_URL'], url_path, miniature)
#
#         if os.path.exists(thumb_filename):
#             return thumb_url
#
#         elif not os.path.exists(thumb_filename):
#             thumb_size = (width, height)
#             try:
#                 image = Image.open(original_filename)
#             except IOError:
#                 return None
#
#             if crop == 'fit':
#                 img = ImageOps.fit(image, thumb_size, Image.ANTIALIAS)
#             else:
#                 img = image.copy()
#                 img.thumbnail((width, height), Image.ANTIALIAS)
#
#             if bg:
#                 img = self._bg_square(img, bg)
#
#             img.save(thumb_filename, image.format, quality=quality)
#
#             return thumb_url
#
#     @staticmethod
#     def _bg_square(img, color=0xff):
#         size = (max(img.size),) * 2
#         layer = Image.new('L', size, color)
#         layer.paste(img, tuple(map(lambda x: (x[0] - x[1]) / 2, zip(size, img.size))))
#         return layer
#
#     @staticmethod
#     def _get_path(full_path):
#         directory = os.path.dirname(full_path)
#
#         try:
#             if not os.path.exists(full_path):
#                 os.makedirs(directory)
#         except OSError as e:
#             if e.errno != errno.EEXIST:
#                 raise
#
#     @staticmethod
#     def _get_name(name, fm, *args):
#         for v in args:
#             if v:
#                 name += '_%s' % v
#         name += fm
#
#         return name
