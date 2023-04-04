from requests.structures import CaseInsensitiveDict

from ..utils import Utils

class Headers:

    '''
    Class to provide request headers as case insensitive dictionaries
    '''

    @classmethod
    def merge(cls, *headers):
        """
        Merge any number of given headers (= dictionaries)
        """
        return Utils.merge_dictionaries(*headers)

    @classmethod
    def x_auth_token(cls, token):
        return CaseInsensitiveDict({'X-Auth-token': token})

    @classmethod
    def accept(cls, accepted):
        return CaseInsensitiveDict({'Accept': accepted})

    @classmethod
    def authorization(cls, auth):
        return CaseInsensitiveDict({'Authorization': auth})

    @classmethod
    def content_type(cls, content_type):
        return CaseInsensitiveDict({'Content-Type': content_type})

    @classmethod
    def accept_json(cls):
        return cls.accept('application/json')
        
    @classmethod
    def content_type_application_json(cls):
        return cls.content_type('application/json')

    @classmethod
    def content_type_application_form(cls):
        return cls.content_type('application/x-www-form-urlencoded')
# flake8: noqa
