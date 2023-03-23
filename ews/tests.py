from django.test import TestCase
from django.urls import reverse

from .helper_classes.Payload import Payload
from .utils import Utils


class IndexViewTests(TestCase):

    def test_mlmodels_reachable(self):
        response = self.client.get(reverse('ews:mlmodels'))
        self.assertEqual(response.status_code, 302)

    def test__bathingspots_reachable(self):
        response = self.client.get(reverse('ews:bathing_spots'))
        self.assertEqual(response.status_code, 302)

    def test_sites_reachable(self):
        response = self.client.get(reverse('ews:sites'))
        self.assertEqual(response.status_code, 302)


# Test with python manage.py test -k UtilsTestCase
class UtilsTestCase(TestCase):

    def setUp(self):
        self.dict = {
            'greeting': 'Hello, {name}',
            'name': '{first_name} {last_name}',
            'last_name': 'Bunny'
        }

    def test_resolve(self):
        """String fields are correctly resolved"""
        f = Utils.lookup_recursively
        self.assertEqual(f('greeting', self.dict), 'Hello, {first_name} Bunny')
        self.assertEqual(f('greeting', self.dict,
                           first_name='Bugs'), 'Hello, Bugs Bunny')
        self.assertEqual(f('x', self.dict), "No such key in dict: 'x'")


# Test with python manage.py test -k PayloadTestCase
class PayloadTestCase(TestCase):

    def test_get_attributes(self):

        self.assertEqual(
            Payload.get_attribute_names(Payload.water_quality_observed),
            ['escherichia_coli', 'dateObserved']
        )

        self.assertEqual(
            Payload.get_attribute_names(Payload.water_observed),
            ['flow', 'dateObserved']
        )

        self.assertEqual(
            Payload.get_attribute_names(Payload.weather_observed),
            ['precipitation', 'dateObserved']
        )
