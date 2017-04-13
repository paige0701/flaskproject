# fabric이 실행할 대상을 제어.

from fabric.api import *

AWS_EC2_01 = 'ec2-52-78-143-155.ap-northeast-2.compute.amazonaws.com'  # Running


PROJECT_DIR = '/var/www/kamper'

APP_DIR = '%s/app' % PROJECT_DIR

"""

# the user to use for the remote commands
env.user = 'appuser'

# the servers where the commands are executed
env.hosts = ['server1.example.com', 'server2.example.com']

"""


env.user = 'kamper'
env.hosts = [AWS_EC2_01]
env.key_filename = '/Users/Mac/Desktop/Genus/1.제품_서비스/KAMP/dev/flask_kamper_package/KAMPERKOREA.pem'


def pack():
    # create a new source distribution as tarball
    local('git checkout')
    # local('git add *')
    local('git commit -a -s -m "Fabric Pack Commit"')


    # local('git push origin master', capture=False)


def deploy():
    print('deploying')
    pass

    # with settings(warn_only=True):
    #     with cd(APP_DIR):
    #         run('sudo ./deploy.sh')

