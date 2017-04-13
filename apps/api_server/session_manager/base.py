from flask import session as flask_session
class BaseSession(object):
    """
    기본 세션
    """
    # session Key MUST BE implemeted
    SESSION_KEY = None

    def __init__(self, session=None):
        if self.SESSION_KEY is None:
            raise NotImplementedError('Session key를 정의해야 합니다.')

        self.session = session

        if self.session is None:
            self.session = flask_session

        if self.SESSION_KEY not in self.session:
            # 없을시 namespace생성
            self.session[self.SESSION_KEY] = {}

    def _check_namespace(self, namespace):
        """
        namespace 있는지 확인
        Ensure a namespace within the session dict is initialised
        """
        if namespace not in self.session[self.SESSION_KEY]:
            self.session[self.SESSION_KEY][namespace] = {}

    def _get(self, namespace, key, default=None):
        """
        Return a value from within a namespace
        """
        self._check_namespace(namespace)
        if key in self.session[self.SESSION_KEY][namespace]:
            return self.session[self.SESSION_KEY][namespace][key]
        return default

    def _set(self, namespace, key, value):
        """
        Set a namespaced value
        """
        self._check_namespace(namespace)
        self.session[self.SESSION_KEY][namespace][key] = value
        self.session.modified = True

    def _unset(self, namespace, key):
        """
            Remove a namespaced value
        """
        self._check_namespace(namespace)
        if key in self.session[self.SESSION_KEY][namespace]:
            del self.session[self.SESSION_KEY][namespace][key]
            self.session.modified = True

    def is_set_namespace(self, namespace):
        if namespace not in self.session[self.SESSION_KEY]:
            return False
        return True

    def _flush_namespace(self, namespace):
        """
        Flush a namespace
        """
        self.session[self.SESSION_KEY][namespace] = {}
        self.session.modified = True

    def flush(self):
        """
        Flush all session data
        """
        self.session[self.SESSION_KEY] = {}

    def get_namespace_dict(self,namespace, default={}):
        self._check_namespace(namespace)
        return dict(self.session[self.SESSION_KEY][namespace])
