import logging
import requests
from ..utils import Utils

# Obtain a logger instance
logger = logging.getLogger('debug')

class AuthenticatedRequest:

    @classmethod
    def lookup_url(cls, key, **kwargs):
        return Utils.lookup_recursively(key, cls.url_grammar, **kwargs)

    # The following three functions
    #
    # - get_authenticated()
    # - post_authenticated()
    # - delte_authenticated()
    #
    # require that the classes that inherit from this class (e.g. CBroker, KRock)
    # implement the function
    #
    # - request_authenticated()

    @classmethod
    def get_authenticated(cls, url):
        '''
        Authenticated GET request to url
        '''
        cls.log_request('GET', url)
        return cls.request_authenticated(requests.get, url)

    @classmethod
    def post_authenticated(cls, url, **kwargs):
        '''
        Authenticated POST request to url
        '''
        cls.log_request('POST', url)
        return cls.request_authenticated(requests.post, url, **kwargs)

    @classmethod
    def delete_authenticated(cls, url):
        '''
        Authenticated DELETE request to url
        '''
        cls.log_request('DELETE', url)
        return cls.request_authenticated(requests.delete, url)

    @classmethod
    def log_request(cls, method, url):
        logger.debug('Authenticated {} request to: {}'.format(method, url))
# flake8: noqa
