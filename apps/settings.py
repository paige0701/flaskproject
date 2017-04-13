"""
config 설정

http://flask.pocoo.org/docs/0.11/config/

"""
import os

import binascii

from flask_babel import gettext as _
from redis import Redis

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.join(BASE_DIR, 'apps')


class BaseConfig(object):
    API_VERSION = '1_1_0'
    APP_NAME = "KAMPER"

    SQLALCHEMY_TRACK_MODIFICATIONS = True

    DEBUG = False
    TESTING = False
    SECRET_KEY = binascii.hexlify(os.urandom(32))
    PERMANENT_SESSION_LIFETIME = 60 * 60
    JSONIFY_PRETTYPRINT_REGULAR = True

    """ FLASK_MAIL """
    MAIL_SERVER = "smtp.worksmobile.com"
    MAIL_PORT = "587"
    MAIL_USE_TLS = True
    # MAIL_USE_SSL = True
    MAIL_USERNAME = 'admin@kamper.co.kr'
    MAIL_PASSWORD = 'us621011'
    MAIL_DEFAULT_SENDER = 'admin@kamper.co.kr'

    """ Flask Babel """
    BABEL_DEFAULT_TIMEZONE = "UTC"
    LANGUAGES = {
        'en': ('English', 'English'),
        'cn': ('Chinese', '中文'),
        'ko': ('Korean', '한국어'),
        'jp': ('Japanese', '日本語'),
        'de': ('Deutsch', 'Deutsch'),

    }
    BABEL_DEFAULT_LOCALE = "en"

    """ FLASK_SECURITY - (https://flask-security.readthedocs.io/en/latest/configuration.html) """
    # SECURITY_CORE
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_PASSWORD_SALT = "3f76a557-01c2-4958-b04d-51cec57bceea"
    SECURITY_EMAIL_SENDER = "admin@kamper.co.kr"
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"
    # SECURITY  URL & VIEWS
    SECURITY_CHANGE_URL = "/change"
    SECURITY_UNAUTHORIZED_VIEW = "/login"  # 403에러
    # SECURITY  Feature Flags
    SECURITY_CONFIRMABLE = False  # 이메일 인증
    SECURITY_TRACKABLE = True
    SECURITY_PASSWORDLESS = False
    SECURITY_CHANGEABLE = True
    # SECURITY_EMAIL
    SECURITY_EMAIL_SUBJECT_REGISTER = _("Welcome to KAMPERKOREA")
    SECURITY_EMAIL_SUBJECT_PASSWORD_NOTICE = _("Instruction on resetting your password")  # password notice. 일어나면 보내는 메일의 Subject
    SECURITY_EMAIL_SUBJECT_PASSWORD_RESET = _("Instruction on resetting your password")
    SECURITY_EMAIL_SUBJECT_PASSWORD_CHANGE_NOTICE = _("Your password has been reset")
    SECURITY_EMAIL_SUBJECT_CONFIRM = _("Confirm email")
    # SECURITY_Miscellaneous
    SECURITY_SEND_REGISTER_EMAIL = True
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = True
    SECURITY_CONFIRM_EMAIL_WITHIN = 5  # email confirm 만료 시간 (days)
    SECURITY_RESET_PASSWORD_WITHIN = '1 hours'  # password reset 만료 시간
    SECURITY_LOGIN_WITHOUT_CONFIRMATION = False  # confirm 하지 않고 사용 할 수 있는 로그인
    SECURITY_RESET_SALT = "1ee10540-8b65-11e6-81c4-87d83ffdeba4"  # Specifies the salt value when generating login links/tokens.
    SECURITY_LOGIN_SALT = "hangang_is_very_good2016-ys25ih27yr24de26jh25jm27sj23dh25team"
    SECURITY_REMEMBER_SALT = "dcb0d3e8-b035-402a-99c1-c0e6533456b7"

    SECURITY_DEFAULT_REMEMBER_ME = True


    # WTF_CSRF_ENABLED = False  # flask token authentication


    # URLs and Views
    # Template Paths
    # Feature Flags
    # Email
    # Miscellaneous

    LANG_CHOICES = {
        'en': _('English'),
        'ko': _('Korean'),
        'cn': _('Chinese')
    }
    PRODUCT_STRUCTURE_CHOICES = {
        'Standalone': _('Stand-alone product'),
        # 'Parent': _('Parent product'),
        # 'Child': _('Child product')
    }

    CART_STATUS_CHOICES = {
        'Open': _("Open - currently active"),
        'Merged': _("Merged - superceded by another basket"),
        'Saved': _("Saved - for items to be purchased later"),
        'Frozen': _("Frozen - the basket cannot be modified"),
        'Submitted': _("Submitted - has been ordered at the checkout")
    }

    ORDER_STATUS_CHOICES = [
        (0, _('Order Completed')),
        (1, _('Payment Completed')),
        (2, _('Shipping')),
        (3, _('Shipping Completed')),
        (4, _('Refund Apply')),
        (5, _('Refund Completed'))
    ]



    # flask s3
    FLASKS3_BUCKET_NAME = 'kamperstatic'
    AWS_ACCESS_KEY_ID = "AKIAISOTMPDO2XRC3MSA"
    AWS_SECRET_ACCESS_KEY = "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"
    FLASKS3_REGION = 'ap-northeast-2'
    USE_S3_DEBUG = True
    FLASKS3_USE_HTTPS = True
    # FLASKS3_GZIP = True
    FLASKS3_ACTIVE = True
    FLASKS3_FORCE_MIMETYPE = True
    FLASKS3_GZIP_ONLY_EXTS = ['.js', '.css', '.less', '.jpg', '.png']

    # custom Flask s3
    MEDIA_FOLDER_TYPE = 's3'
    FLASKS3_MEDIA_BUCKET_NAME = 'kamper-mediafiles'
    FLASKS3_MEDIA_BUCKET_ROOT = 'media'

    ##### Flask-redis #####
    REDIS_SESSION_HOST = "52.79.47.181"
    REDIS_SESSION_PORT = "6379"
    REDIS_SESSION_PASSWORD = "flask-kamper"
    REDIS_SESSION_DB = "0"
    session_redis = Redis(host=REDIS_SESSION_HOST, password=REDIS_SESSION_PASSWORD,
                          port=REDIS_SESSION_PORT, db=REDIS_SESSION_DB)

    #### FLASK SESSION ####
    # https: // github.com / fengsp / flask - session
    # http: // pythonhosted.org / Flask - Session /
    SESSION_TYPE = 'redis'

    SESSION_USE_SIGNER = False
    SESSION_KEY_PREFIX = 'session:'
    SESSION_REDIS = session_redis

    # SESSION_REDIS = '6379'
    # A memcache.Client instance, default connect to 127.0.0.1:11211

    # Flask-Thumbnail Configuration
    MEDIA_TYPE = 's3'
    MEDIA_BUCKET_NAME = 'kamper-mediafiles'
    MEDIA_ROOT = 'media'
    MEDIA_REGION = 'ap-northeast-2'
    THUMBNAIL_ROOT = 'thumbnail'

    # URL
    BASE_URL = 'http://127.0.0.1:5000'


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    # SQLALCHEMY Configuration
    SQLALCHEMY_DATABASE_URI = 'mysql://kamper:kamp12!!@kamper.cdicxkxbkujf' \
                              '.ap-northeast-2.rds.amazonaws.com:3307/kamper_development'
    # Flask-redis
    # REDIS_SESSION_HOST = "52.78.231.29"
    # REDIS_SESSION_PORT = "6379"
    # REDIS_SESSION_PASSWORD = ""
    # REDIS_SESSION_DB = "0"

    MEDIA_FOLDER = 'media'
    MEDIA_PATH = os.path.join(BASE_DIR, MEDIA_FOLDER)




    # REDIS_URL = "redis://:@52.78.102.124:6379/0"


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True


class ProductionDevelopmentConfig(DevelopmentConfig):
    SQLALCHEMY_DATABASE_URI = "mysql://kamper:kamp12!!@kamper.cvw58cnqxxtv.ap-northeast-2.rds.amazonaws.com:3306/" \
                              "kamper_production"



class ProductionConfig(DevelopmentConfig):
    "kamper.cvw58cnqxxtv.ap-northeast-2.rds.amazonaws.com"
    DEBUG = False
    TESTING = False
    BASE_URL = 'https://www.kamper.co.kr'
    SQLALCHEMY_DATABASE_URI = "mysql://kamperkorea:kamp12!!@kamper.cvw58cnqxxtv.ap-northeast-2.rds.amazonaws.com:3306/" \
                              "KAMPER"

    # SQLALCHEMY_DATABASE_URI = 'mysql://kamper:kamp12!!@kamperflaskdeveloper2test.cdicxkxbkujf' \
    #                           '.ap-northeast-2.rds.amazonaws.com/kamper_development'

    # 보류
    ##### Flask-redis #####
    # REDIS_SESSION_HOST = "kamper-session.fu7umk.0001.apn2.cache.amazonaws.com"
    # REDIS_SESSION_PORT = "6379"
    # REDIS_SESSION_PASSWORD = ""
    # REDIS_SESSION_DB = "0"
    # session_redis = Redis(host=REDIS_SESSION_HOST, password=REDIS_SESSION_PASSWORD,
    #                       port=REDIS_SESSION_PORT, db=REDIS_SESSION_DB)
