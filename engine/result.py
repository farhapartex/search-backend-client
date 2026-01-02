class ServiceResult:

    def __init__(self, success, data=None, message=None, errors=None):
        self.success = success
        self.data = data
        self.message = message
        self.errors = errors

    @classmethod
    def ok(cls, data=None, message=None):
        return cls(success=True, data=data, message=message)

    @classmethod
    def fail(cls, message, errors=None):
        return cls(success=False, message=message, errors=errors)

    def to_dict(self):
        result = {'success': self.success}

        if self.message:
            result['message'] = self.message

        if self.data:
            result['data'] = self.data

        if self.errors:
            result['errors'] = self.errors

        return result
