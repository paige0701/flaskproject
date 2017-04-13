import mimetypes
import os

import boto3
from flask import current_app as app, current_app, url_for
from flask_security import current_user

#
ALLOWED_IMAGE_EXTENSION = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_image_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSION


def upload_s3_mediafile(file, filepath):
    """
    참고자료 https://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Bucket.upload_fileobj
    :param file: fileStorage
    :parm base: mediafile  - app.config.get('FLASKS3_MEDIA_BUCKET_ROOT')
    :param filepath: 저장될 file path (key)
    :return:
    """

    filepath = os.path.join('media', filepath)
    s3_resource = boto3.resource('s3',
                                 app.config['FLASKS3_REGION'],
                                 # Hard coded strings as credentials, not recommended.
                                 aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'),
                                 aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY')
                                 )

    s3_media_bucket = s3_resource.Bucket(app.config.get('FLASKS3_MEDIA_BUCKET_NAME'))

    mimetype = None
    if mimetype is None and (filepath):
        mimetype = mimetypes.guess_type(filepath)[0]
    if mimetype is None:
        mimetype = 'application/octet-stream'

    # 같은 이름의 파일이 있는지 확인.
    s3_media_bucket.upload_fileobj(file, filepath, ExtraArgs={'ContentType': mimetype})

    return filepath



def url_for_s3(endpoint, bucket_name=None, scheme='https', bucket_domain=None, url_style='host', cdn_domain=None,
               filename=None):
    """
    https://kamperstatic.s3.amazonaws.com/static/bower_components/jquery/dist/jquery.min.js
             <bucketname>                 <path>
    :param endpoint:
    :param scheme:  http/ https
    :param bucket_domain: s3.amazonaws.com
    :param url_style: host방식 (라우트 위함
    :param cdn_domain:
    :param bucket_name: 버킷이름. default(settings > FLASKS3_MEDIA_BUCKET_NAME)
    :param filename:
    :return:
    """
    if not bucket_name:
        bucket_name = current_app.config['FLASKS3_MEDIA_BUCKET_NAME']
        if not bucket_name:
            raise ValueError('Bucket name is required when calling url_for_media().')

    if url_style == 'host':
        url_format = '%(bucket_name)s.%(bucket_domain)s'
    elif url_style == 'path':
        url_format = '%(bucket_domain)s/%(bucket_name)s'
    else:
        raise ValueError('Invalid S3 URL Style: "%s"')

    if bucket_domain is None:
        bucket_domain = 's3.amazonaws.com'
        bucket_path = url_format % {
            'bucket_name': bucket_name,
            'bucket_domain': bucket_domain,
        }

    if cdn_domain:
        bucket_path = "%s" % cdn_domain

    return str("%s//%s/%s%s" % (
        scheme + (':' if scheme else ''),
        bucket_path,
        endpoint + ('/' if endpoint else ''),
        filename.lstrip('/')
    ))

# 오직 private media
def get_s3_url(filename, method='public'):
    _available_method = ('public', 'private', )

    if method not in _available_method:
        raise AttributeError('_avalilable method는 반드시 %s에 속해 있어야 합니다' % _available_method)
    if filename is None:
        raise ValueError('File 이름은 None이면 안돼!')

    if method == 'public':
        return url_for_s3('media', filename=filename)
    elif method == 'private':

        user = current_user
        if user.is_authenticated and (user.has_role('superuser')):
            return url_for('private_media', filename=filename)
        else:
            return url_for_s3('media', filename=filename)

