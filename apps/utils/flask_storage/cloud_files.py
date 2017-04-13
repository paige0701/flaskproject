__version__ = '0.0.0'
__author__ = 'KAMPER'


class CloudFileStorage(object):
    """
    useful utility for Flask Media(For uploading) File save, delete, update ..
    in Cloud service like (AWS-s3, Azure, GAE ...)

    if you want to control just static files Just use the other extensions(like Flask-s3)
    """

    # 1. cloud_type.
    # 2. cloud_endpoint
    # 3. cloud_bucketname (storage_name)
    # 4. cloud_key_id
    # 5. cloud_key_secret


    def __init__(self, app=None, cloud_type=None, cloud_endpoint=None, cloud_bucket_name=None, cloud_key_id=None,
                 cloud_key_secret=None):
        if app is not None:
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        self.app = app

    def save_file(self):
        raise NotImplementedError

    def delete_file(self):
        raise NotImplementedError

    def update_file(self):
        raise NotImplementedError

    def generate_name(self):
        """
        Making generate file name for Secure file name
        :return:
        """
        raise NotImplementedError

    def pre_validate(self):
        """
        validation
        :return:
        """
        raise NotImplementedError
