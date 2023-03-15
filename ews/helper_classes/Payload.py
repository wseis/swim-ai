import logging
from pprint import pformat

# Obtain a logger instance
logger = logging.getLogger('debug')


class Payload():

    @classmethod
    def string_value(cls, value):
        return {'type': 'string', 'value': value}

    @classmethod
    def default_date_value(cls):
        return cls.string_value('1970-01-01 00:00:00')

    @classmethod
    def float_value(cls, value):
        return {'value': value, 'type': 'Float'}

    @classmethod
    def water_quality_predicted(cls, model_id, model_name):
        return {
            'id': ('urn:ngsi-ld:WaterQualityPredicted:' +
                   str(model_id) + ':' + str(model_name)),
            'type': 'WaterQualityPredicted',
            'precipitation': cls.float_value(0),
            'dateCreated': cls.default_date_value(),
            'datePredicted': cls.default_date_value(),
            'waterQualityClassification': cls.string_value('excellent'),
            'percentile2_5': cls.float_value(0.025),
            'percentile50': cls.float_value(0.5),
            'percentile90': cls.float_value(0.9),
            'percentile95': cls.float_value(0.95),
            'percentile97_5': cls.float_value(0.975),
        }

    @classmethod
    def water_observed(cls, broker_id, broker_type):
        return {
            'id': broker_id,
            'type': broker_type,
            'flow': cls.float_value(0),
            'dateObserved': cls.default_date_value()
        }

    @classmethod
    def weather_observed(cls, broker_id, broker_type):
        return {
            'id': broker_id,
            'type': broker_type,
            'precipitation': cls.float_value(0),
            'dateObserved': cls.default_date_value()
        }

    @classmethod
    def water_quality_observed(cls, broker_id, broker_type):
        return {
            'id': broker_id,
            'type': broker_type,
            'escherichia_coli': cls.float_value(0),
            'dateObserved': cls.default_date_value()
        }

    @classmethod
    def get_attribute_names(cls, payload_fun):
        '''
        Which attribute names (except for "id" and "type")
        does the object provide that
        is returned by the function given in payload_fun?
        '''
        # Call the function with fake values for broker_id and broker_type.
        payload = payload_fun(broker_id=-1, broker_type="none")

        # Return the names of the keys, excluding "id" and "type"
        attributes = list(payload.keys())[2:]

        logger.debug('Determined attribute names: ' + pformat(attributes))

        return attributes
