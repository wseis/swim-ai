import json
import logging
import pandas
import requests

from decouple import config
from oauthlib.oauth2 import BackendApplicationClient
from pprint import pformat
from requests_oauthlib import OAuth2Session

from .AuthenticatedRequest import AuthenticatedRequest
from .Headers import Headers
from ..utils import Utils

# Obtain a logger instance
logger = logging.getLogger('debug')

class KRockError(Exception):
    """Exception raised for errors reported by KRock."""

    def __init__(self, message="Error in K-Rock"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'

class KRock(AuthenticatedRequest):

    url_grammar = {
        'base': 'https://k-rock.xyz',
        'oauth2_token': '{base}/oauth2/token',
        'base_v': '{base}/v{api_version}',
        'auth_tokens': '{base_v}/auth/tokens',
        'users': '{base_v}/users',
        'app': '{base_v}/applications/{app_id}',
        'app_users': '{app}/users',
        'app_roles': '{app}/roles',
        'app_permissions': '{app}/permissions',
        'app_user_role': '{app_users}/{user_id}/roles/{role_id}',
        'app_role_permissions': '{app_roles}/{role_id}/permissions/{permission_id}',
        'api_version': '1'
    }

    # Member functions inherited from AuthenticatedRequest:
    # - lookup_url(cls, key, **kwargs):
    # - get_authenticated(cls, url, **kwargs):
    # - post_authenticated(cls, url, **kwargs):

    @classmethod
    def get_token(cls):
        response = requests.post(
            cls.lookup_url('oauth2_token'),
            headers=Headers.merge(
                Headers.content_type_application_form(),
                Headers.accept_json(),
                Headers.authorization('Basic ' + config('AUTH_BASIC'))
            ),
            data={
                'username': config('KEYROCK_ADMIN'),
                'password': config('KEYROCK_PW'),
                'grant_type': 'password'
            }
        )

        Utils.debug_response_status(
            logger,
            response,
            'KRock::get_token() returned:'
        )

        return response.json()['access_token']

    @classmethod
    def get_clientCredential_token(cls):
        client_id = config('CLIENT_ID')
        session = OAuth2Session(client=BackendApplicationClient(client_id))
        return session.fetch_token(
            token_url=cls.lookup_url('oauth2_token'),
            client_id=client_id,
            client_secret=config('CLIENT_SECRET')
        )

    @classmethod
    def get_admin_token(cls):
        response = requests.post(
            cls.lookup_url('auth_tokens'),
            headers=Headers.content_type_application_json(),
            data=json.dumps({
                'name': config('KEYROCK_ADMIN'),
                'password': config('KEYROCK_PW')
            })
        )
        return response.headers['X-Subject-Token']

    @classmethod
    def request_authenticated(cls, method, url, **kwargs):
        '''
        Authenticated request to url
        '''
        return method(
            url,
            headers=Headers.merge(
                Headers.content_type_application_json(),
                Headers.x_auth_token(cls.get_admin_token())
            ),
            **kwargs
        )

    @classmethod
    def create_user_and_role(cls, app_id, username_keyrock, pw_keyrock, email_keyrock):

        # Create a user
        user = cls.create_user(
            username=username_keyrock,
            email=email_keyrock,
            password=pw_keyrock
        )

        # Create a role corresponding to the username
        role = cls.create_role(
            app_id=app_id,
            username=username_keyrock
        )

        user_json = user.json()
        role_json = role.json()

        logger.debug("user.json(): " + pformat(user_json))
        logger.debug("role.json(): " + pformat(role_json))

        if "error" in user_json:
            raise KRockError(user_json['error']['message'])

        if "error" in role_json:
            raise KRockError(role_json['error']['message'])

        # Assign the created user to the created role
        user_role = cls.assign_user_to_role(
            app_id=app_id,
            user_id=user_json['user']['id'],
            role_id=role_json['role']['id']
        )

        return user_role.json()

    @classmethod
    def create_and_assign_permissions(cls, app_id, broker_id, resource, resource_owner):

        # Ask K-Rock for all roles that are defined for this app
        response_roles = cls.get_roles(app_id=app_id)

        # Convert to data frame
        df_roles = pandas.json_normalize(response_roles.json()['roles'])

        #permissions = []
        #for site in site.iterator():

        # Tell K-Rock that the context broker is allowed to use this app (?)
        response_permission = cls.set_permissions(
            app_id=app_id,
            name=broker_id,
            resource=resource
        )

        #permissions.append(response.json()['permission']['id'])
        #for permission in permissions:

        # Let K-Rock connect role and permission (?)
        response = cls.set_role_permissions(
            app_id=app_id,
            role_id=df_roles[df_roles['name'] == resource_owner].id.values[0],
            permission_id=response_permission.json()['permission']['id']
        )

        return response.json()

    @classmethod
    def create_user(cls, username, email, password):
        return cls.post_authenticated(
            cls.lookup_url('users'),
            data=json.dumps({'user': {'username': username, 'email': email, 'password': password}})
        )

    @classmethod
    def get_roles(cls, app_id):
        return cls.get_authenticated(
            cls.lookup_url('app_roles', app_id=app_id)
        )

    @classmethod
    def create_role(cls, app_id, username):
        return cls.post_authenticated(
            cls.lookup_url('app_roles', app_id=app_id),
            data=json.dumps({'role': {'name': username}})
        )

    @classmethod
    def assign_user_to_role(cls, app_id, user_id, role_id):
        return cls.post_authenticated(
            cls.lookup_url('app_user_role', app_id=app_id, user_id=user_id, role_id=role_id)
        )

    @classmethod
    def set_permissions(cls, app_id, name, resource):
        return cls.post_authenticated(
            cls.lookup_url('app_permissions', app_id=app_id),
            data=json.dumps({'permission': {'name': name, 'action': 'PATCH', 'resource': resource}})
        )

    @classmethod
    def set_role_permissions(cls, app_id, role_id, permission_id):
        return cls.post_authenticated(
            cls.lookup_url(
                'app_role_permissions', 
                app_id=app_id, 
                role_id=role_id, 
                permission_id=permission_id
            )
        )
