from flask_security import current_user

"""
Authorize에 권한 을제공
"""


class SuperuserMixIn(object):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if 'superuser' in current_user.roles:
            return True

        return False


class StaffMixIn(object):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        if 'superuser' in current_user.roles or 'staff' in current_user.roles:
            return True
        return False


class PartnerMixIn(object):
    """
    partner_roles : 파트너일 경우의 role을 뜻한다.
    """
    partner_roles = None

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        if 'superuser' in current_user.roles or 'staff' in current_user.roles or 'partner' in current_user.roles:
            return True
        return False

    def get_role_name(self):
        if 'superuser' in current_user.roles:
            return 'superuser'
        elif 'staff' in current_user.roles:
            return 'staff'
        elif self.partner_roles in current_user.roles:
            return 'partner'
        return False



