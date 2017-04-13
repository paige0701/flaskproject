from flask_testing import TestCase

from apps import app, db
from core.auth import User


class MyTest(TestCase):
    TESTING = True

    def create_app(self):
        app.config.from_object("test_apps.settings.TestingConfig")
        # pass in test configuration
        return app

    def setUp(self):
        db.create_all()




    def test_adduser(self):

        user = User(email="test@test.com", password="123", first_name="first", last_name='last')
        user2 = User(email="lucas@test.com", password="456",first_name='fname', last_name='lname')

        db.session.add(user)
        db.session.commit()

        assert user in db.session
        assert user2 not in db.session

    def tearDown(self):
        db.session.remove()
        db.drov.data

