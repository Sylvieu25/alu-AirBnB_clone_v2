#!/usr/bin/python3
""" Unit tests for State """
from tests.test_models.test_base_model import test_basemodel
from models.city import City
from models.state import State
import os
import unittest


class test_state(test_basemodel):
    """ Tests for State """

    def __init__(self, *args, **kwargs):
        """ Set the class under test """
        super().__init__(*args, **kwargs)
        self.name = "State"
        self.value = State

    def test_name3(self):
        """ name is stored as a string """
        new = self.value(name="California")
        self.assertEqual(type(new.name), str)

    @unittest.skipIf(os.getenv('HBNB_TYPE_STORAGE') == 'db',
                     'FileStorage only')
    def test_cities_filestorage(self):
        """ cities returns only the cities linked to this state """
        state = State(name="California")
        state.save()
        city = City(name="San Francisco", state_id=state.id)
        city.save()
        other = City(name="Reno", state_id="another-state")
        other.save()
        city_ids = [c.id for c in state.cities]
        self.assertIn(city.id, city_ids)
        self.assertNotIn(other.id, city_ids)
