import os
import tempfile
import unittest



class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, kamper.app.config['DATABASE'] = tempfile.mkstemp()
        kamper.app.config['TESTING'] = True
        self.app = kamper.app.test_client()
        # kamper.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(kamper.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert 'helloworld' in rv.data

if __name__ == '__main__':
    unittest.main()