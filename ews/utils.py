import logging
import string

# Obtain a logger instance
logger = logging.getLogger('debug')

class Utils:

    @classmethod
    def lookup_recursively(cls, key, dict, **kwargs):
        '''
        Extend the dictionary with the key=value pairs given in
        kwargs and lookup the value for key in the extended dictionary
        (by replacing all {fields} recursively)
        '''
        #logger.debug('Looking up recursively: "{}"'.format(key))
        if not key in dict:
            resolved = "No such key in dict: '{}'".format(key)
        else:
            resolved = cls.resolve(dict[key], {**dict, **kwargs})
        #logger.debug('Resolved: "{}"'.format(resolved))
        return resolved

    @classmethod
    def get_fields(cls, s):
        '''
        Get names of {fields} in string s
        '''
        names = [name for text, name, spec, conv in string.Formatter().parse(s)]
        return list(filter(None, names))

    @classmethod
    def resolve(cls, s, dict = {}, depth = 1, max_depth = 10):
        '''
        Resolve {fields} in string s, looking up their values in dict
        '''
        if depth > max_depth:
            print("Maximum recursion depth ({}) reached.".format(max_depth))
            return s

        fields = cls.get_fields(s)

        if not fields:
            return s

        args = {}

        for field in fields:
            args[field] = cls.resolve(
                # If name is not in the dictionary, restore the "{field}"
                dict.get(field, '{' + field + '}'),
                dict, depth + 1,
                max_depth = max_depth
            )

        return s.format(**args)

    @classmethod
    def merge_dictionaries(cls, *dictionaries):
        """
        Given any number of dictionaries, shallow copy and merge into a new dict,
        precedence goes to key-value pairs in latter dictionaries.
        See https://stackoverflow.com/questions/38987/how-do-i-merge-two-dictionaries-in-a-single-expression-take-union-of-dictionari
        """
        result = {}
        for dictionary in dictionaries:
            result.update(dictionary)
        return result

    @classmethod
    def debug_response_status(cls, logger, response, caption):
        logger.debug(caption)
        logger.debug('  status_code: {}'.format(response.status_code))
        logger.debug('  reason: {}'.format(response.reason))
        logger.debug('  text: {}'.format(response.text))
