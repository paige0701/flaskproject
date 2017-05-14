import mimetypes
from datetime import datetime, timedelta
import time

import boto3
import botocore

from flask_sqlalchemy import SQLAlchemy
from flask_security import SQLAlchemyUserDatastore
from redis import Redis
from flask import abort,send_from_directory, redirect, current_app, g, request, render_template, make_response
from flask_security import current_user

from apps.core.redis_session import RedisSessionInterface

app = Flask(__name__)

app.config.from_object('apps.settings.DevelopmentConfig')
# app.config.from_object('apps.settings.ProductionConfig')

# sesson_redis 연결
# session_redis = Redis(host=app.config['REDIS_SESSION_HOST'], password=app.config['REDIS_SESSION_PASSWORD'],
#                       port=app.config['REDIS_SESSION_PORT'], db=app.config['REDIS_SESSION_DB'])
# app.session_interface = RedisSessionInterface(session_redis)

# db instance 초기화
db = SQLAlchemy(app)

# register_extensions and register_blueprints
from .smart_registration import register_extensions, register_blueprints, register_errorhandlers

register_extensions(app)
register_blueprints(app)
register_errorhandlers(app)

from apps.api_server.services.housing_service.models import Type, Housing, Room


@app.route('/set_locale', methods=['GET'])
def set_locale():
    # lang_code = request.form.get('lang_code')
    lang_code = request.args.get('lang_code')
    print("지금 무슨 언어로 되어 있니 ?? === ",lang_code)
    redirect_to_index = redirect(request.referrer)
    response = current_app.make_response(redirect_to_index)
    response.set_cookie('locale_lang', value=lang_code, expires=datetime.now() + timedelta(days=365))

    return response


@app.errorhandler(500)
def error_500():
    return redirect(url_for('web_common.index'))

# from apps.utils.crawl import crawl_wemakeprice_detail
#
# @app.route('/temp')
# def temo():
#     # soup = crawl_wemakeprice_detail('deal/adeal/1563919/')
#     soup = crawl_wemakeprice_detail('deal/adeal/1580201')
#
#     return render_template('temp.html', code=soup)
#




# print(responsed)
# lang_code = request.accept_languages.best_match(app.config['LANGUAGES'].keys())
# responsed.set_cookie('locale_lang', value=lang_code)
# print(responsed)


#
# @app.route('/media/<path:filename>')
# def media(filename):
#     """
#     임시메소드 추후 변경해야함!!
#     -> redirect로 처리했기 때문
#     :param filename:
#     :return:
#     """
#     print('kkkk')
#     # media = app.config['FLASKS3_MEDIA_BUCKET_NAME']
#     # app.config['AWS_SECRET_ACCESS_KEY']
#     # app.config['AWS_ACCESS_KEY_ID']
#     FLASKS3_MEDIA_BUCKET_NAME = 'kamper-mediafiles'
#     file = get_s3_mediafile(filename)
#     #
#     return file
#
#     # return redirect("https://%s.s3.amazonaws.com/%s" %(FLASKS3_MEDIA_BUCKET_NAME, filename))
#     # return redirect("https://s3.ap-northeast-2.aazonaws.com/%s/%s" % (FLASKS3_MEDIA_BUCKET_NAME, filename))
#     # return send_from_directory(app.config['MEDIA_FOLDER'], filename)


from apps.utils.file_manager import url_for_s3



@app.route('/private_media/<path:filename>')
def private_media(filename):
    user= current_user

    if not(user.is_authenticated and (user.has_role('superuser'))):
        return abort(404)

    b_name = current_app.config.get('MEDIA_BUCKET_NAME')

    # 권한에 맞는 s3를 불러온다
    s3 = get_approved_s3()

    bucket = s3.Bucket(b_name)
    obj = bucket.Object(filename)

    try:
        resp = obj.get()

        response = make_response(resp.get('Body').read())

        mimetype = resp.get('content-type')

        if not mimetype or mimetype == 'application/octet-stream':
            mimetype = mimetypes.guess_type(filename)[0]
            if mimetype is None:
                mimetype = 'application/octet-stream'

        response.headers['Content-Type'] = mimetype

    except botocore.exceptions.ClientError:
        return abort(401)

    return response

# ----------------------------------------------------------------------------------------------------------------
# Time 체크용 타임 체크용
# ----------------------------------------------------------------------------------------------------------------
# def private_media(filename):
#     first_time = time.process_time()
#
#     start_time = time.process_time() *10000
#     user= current_user
#     if not(user.is_authenticated and (user.has_role('superuser'))):
#         return abort(404)
#     print("---user 권한 검사 %s seconds ---" % (time.process_time()*10000 - start_time))
#
#     start_time = time.process_time()*10000
#     b_name = current_app.config.get('MEDIA_BUCKET_NAME')
#
#     # 권한에 맞는 s3를 불러온다
#     s_time = time.process_time() *10000
#     s3 = get_approved_s3()
#     print("---승인 검사 %s seconds ---" % (time.process_time()*10000 - s_time))
#
#
#
#     bucket = s3.Bucket(b_name)
#     obj = bucket.Object(filename)
#     print("---s3 bucket 가져오는 검사 %sseconds ---" % (time.process_time()*10000 - start_time))
#
#     try:
#         start_time = time.process_time() * 10000
#         resp = obj.get()
#         print("---이미지지 가져는 검사 %s seconds ---" % (time.process_time() * 10000 - start_time))
#
#         start_time = time.process_time()
#         response = make_response(resp.get('Body').read())
#         print("---이미지 읽는 검사 %s seconds ---" % (time.process_time() - start_time))
#
#
#         start_time = time.process_time() * 10000
#         mimetype = resp.get('content-type')
#
#         if not mimetype or mimetype == 'application/octet-stream':
#             mimetype = mimetypes.guess_type(filename)[0]
#             if mimetype is None:
#                 mimetype = 'application/octet-stream'
#
#         response.headers['Content-Type'] = mimetype
#         print("---response 만드는 검사 %s seconds ---" % (time.process_time() * 10000 - start_time))
#
#     except botocore.exceptions.ClientError:
#         return abort(401)
#
#     print("--%s 총 시간 %s seconds" %(filename, time.process_time()- first_time))
#
#     return response


def get_approved_s3():
    user = current_user
    if user.is_authenticated and (user.has_role('superuser')):
        return boto3.resource('s3', app.config['FLASKS3_REGION'],
                              aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'),
                              aws_secret_access_key = app.config.get('AWS_SECRET_ACCESS_KEY'))
    else:
        return boto3.resource('s3', app.config['FLASKS3_REGION'])




#
# """
#     # print('-====')
#     # print('obj.accept_ranges: ',obj.accept_ranges)
#     # print('obj.cache_control: ',obj.cache_control)
#     # print('obj.content_disposition: ',obj.content_disposition)
#     # print('obj.content_encoding: ',obj.content_encoding)
#     # print('obj.content_language: ',obj.content_language)
#     # print('obj.content_length: ',obj.content_length)
#     # print('obj.content_type: ',obj.content_type)
#     # print('obj.delete_marker: ',obj.delete_marker)
#     # print('obj.e_tag: ',obj.e_tag)
#     # print('obj.expiration: ',obj.expiration)
#     # print('obj.expires: ',obj.expires)
#     # print('obj.last_modified: ',obj.last_modified)
#     # print('obj.metadata: ',obj.metadata)
#     # print('obj.missing_meta: ',obj.missing_meta)
#     # print('obj.parts_count: ',obj.parts_count)
#     # print('obj.replication_status: ',obj.replication_status)
#     # print('obj.request_charged: ',obj.request_charged)
#     # print('obj.restore: ',obj.restore)
#     # print('obj.server_side_encryption: ',obj.server_side_encryption)
#     # print('obj.sse_customer_algorithm: ',obj.sse_customer_algorithm)
#     # print('obj.sse_customer_key_md5: ',obj.sse_customer_key_md5)
#     # print('obj.ssekms_key_id: ',obj.ssekms_key_id)
#     # print('obj.storage_class: ',obj.storage_class)
#     # print('obj.version_id: ',obj.version_id)
#     # print('obj.website_redirect_location: ',obj.website_redirect_location)
# """

app.jinja_env.globals['url_for_s3'] = url_for_s3

from flask import url_for


@app.context_processor
def inject_debug():
    return dict(debug=app.debug)
