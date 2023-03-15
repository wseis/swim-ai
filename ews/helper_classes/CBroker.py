import logging

from .AuthenticatedRequest import AuthenticatedRequest
from .Headers import Headers
from .KRock import KRock
from .Payload import Payload
from ..utils import Utils

# Obtain a logger instance
logger = logging.getLogger('debug')


class CBroker(AuthenticatedRequest):

    url_grammar = {
        'api_version': '2',
        'base': 'https://www.c-broker.xyz',
        'rel_v': '/v{api_version}',
        'rel_entities': '{rel_v}/entities',
        'rel_broker': '{rel_entities}/{broker_id}',
        'rel_broker_attributes': '{rel_broker}/attrs',
        'entities': '{base}{rel_entities}',
        'entity': '{base}{rel_broker}',
        'subscriptions': '{base}{rel_v}/subscriptions',
        'subscription': '{subscriptions}/{subscription_id}',
        'water_quality': ('{entities}/urn:ngsi-ld:WaterQualityPredicted:'
                          '{model_id}:{model_name}'),
        'slug_attributes': '{entities}/{slug}/attrs',
        'import_new_data': ('https://www.dwc-ds2.xyz/import_new_data/',
                            '{subscription_url}')
    }

    # Member functions inherited from AuthenticatedRequest:
    # - lookup_url(cls, key, **kwargs):
    # - get_authenticated(cls, url):
    # - post_authenticated(cls, url, **kwargs):
    # - delete_authenticated(cls, url):

    @classmethod
    def request_authenticated(cls, method, url, **kwargs):
        '''
        Authenticated request to url
        '''
        response = method(
            url,
            headers=Headers.x_auth_token(KRock.get_token()),
            verify=False,
            **kwargs
        )

        Utils.debug_response_status(
            logger,
            response,
            'CBroker::request_authenticated("{}") returned:'.format(url)
        )

        return response

    @classmethod
    def get_subscriptions(cls):
        return cls.get_authenticated(cls.lookup_url('subscriptions'))

    @classmethod
    def get_slug_attributes(cls, slug):
        return cls.get_authenticated(cls.lookup_url('slug_attributes',
                                                    slug=slug))

    @classmethod
    def post_entities(cls, json):
        return cls.post_authenticated(cls.lookup_url('entities'),
                                      json=json)

    @classmethod
    def post_water_quality_predicted(cls, model_id, model_name):
        return cls.post_entities(
            Payload.water_quality_predicted(model_id, model_name)
        )

    @classmethod
    def post_water_observed(cls, broker_id, broker_type):
        return cls.post_entities(
            Payload.water_observed(broker_id, broker_type)
        )

    @classmethod
    def post_weather_observed(cls, broker_id, broker_type):
        return cls.post_entities(
            Payload.weather_observed(broker_id, broker_type)
        )

    @classmethod
    def post_water_quality_observed(cls, broker_id, broker_type):
        return cls.post_entities(
            Payload.water_quality_observed(broker_id, broker_type)
        )

    @classmethod
    def subscribe(cls, broker_id, broker_type,
                  subscription_url, payload_fun):
        # The attribute names that are required
        # for the subscription record are read
        # from the object that is returned by the given payload function
        attributes = Payload.get_attribute_names(payload_fun)
        json = cls.subscription_record(broker_id,
                                       broker_type,
                                       subscription_url,
                                       attributes)
        return cls.post_authenticated(cls.lookup_url('subscriptions'),
                                      json=json)

    @classmethod
    def subscribe_water_observed(cls, broker_id,
                                 broker_type, subscription_url):
        return cls.subscribe(broker_id, broker_type,
                             subscription_url,
                             payload_fun=Payload.water_observed)

    @classmethod
    def subscribe_weather_observed(cls, broker_id,
                                   broker_type, subscription_url,):
        return cls.subscribe(broker_id, broker_type,
                             subscription_url,
                             payload_fun=Payload.weather_observed)

    @classmethod
    def subscribe_water_quality_observed(cls, broker_id,
                                         broker_type, subscription_url):
        return cls.subscribe(broker_id, broker_type,
                             subscription_url,
                             payload_fun=Payload.water_quality_observed)

    @classmethod
    def subscription_record(cls, broker_id,
                            broker_type, subscription_url,
                            attributes):
        return {
            'description': broker_id,
            'subject': {
                'entities': [{'id': broker_id, 'type': broker_type}],
                'condition': {'attrs': attributes}
            },
            'notification': {
                'http': ({'url': cls
                          .lookup_url('import_new_data',
                                      subscription_url=subscription_url)})
            }
        }

    @classmethod
    def delete_broker(cls, broker_id):
        return cls.delete_authenticated(
            cls.lookup_url('entity', broker_id=str(broker_id))
        )

    @classmethod
    def delete_subscription(cls, subscription_id):
        return cls.delete_authenticated(
            cls.lookup_url('subscription', subscription_id=subscription_id)
        )

    @classmethod
    def delete_water_quality(cls, model_id, model_name):
        return cls.delete_authenticated(
            cls.lookup_url('water_quality', model_id=str(model_id),
                           model_name=model_name)
        )

    @staticmethod
    def feature_type_to_broker_type(feature_type_name):
        if feature_type_name in ['WWTP', 'Network', 'Riverflow']:
            return 'WaterObserved'
        if feature_type_name in ['Rainfall']:
            return 'WeatherObserved'
        if feature_type_name in ['BathingSpot']:
            return 'WaterQualityObserved'
        raise NameError('Unknown feature type: ' + feature_type_name)
