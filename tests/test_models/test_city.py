#!/usr/bin/python3
""" Unit tests for City """
from tests.test_models.test_base_model import test_basemodel
from models.city import City


class test_City(test_basemodel):
    """ Tests for City """

    def __init__(self, *args, **kwargs):
        """ Set the class under test """
        super().__init__(*args, **kwargs)
        self.name = "City"
        self.value = City

    def test_state_id(self):
        """ state_id is stored as a string """
        new = self.value(state_id="0001")
        self.assertEqual(type(new.state_id), str)

    def test_name(self):
        """ name is stored as a string """
        new = self.value(name="San Francisco")
        self.assertEqual(type(new.name), str)
