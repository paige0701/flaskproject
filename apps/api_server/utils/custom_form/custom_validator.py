
class Validate_Text_Type(object):
    _text_type = ('number')

    def __init__(self, text_type='number', message=None):
        if text_type not in self._text_type:
            raise ValueError('지정된 text_type이 아닙니다. 반드시 %s 중에 입력하여야 합니다.' % self._text_type)
        self.text_type = text_type
        if not message:
            message = 'Field must be only %s' % self.text_type
        self.message = message

    def __call__(self, form, field):
        data = field.data
        if self.text_type == 'number':
            if not self.is_number(data):
                raise ValidationError(self.message)

    def is_number(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False
        except TypeError:
            return False

validate_text_type = Validate_Text_Type