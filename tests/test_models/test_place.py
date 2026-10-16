#!/usr/bin/python3
""" Unit tests for Place """
from tests.test_models.test_base_model import test_basemodel
from models import storage
from models.city import City
from models.place import Place
from models.state import State
from models.user import User
import os
import unittest


class test_Place(test_basemodel):
    """ Tests for Place """

    def __init__(self, *args, **kwargs):
        """ Set the class under test """
        super().__init__(*args, **kwargs)
        self.name = "Place"
        self.value = Place

    def test_city_id(self):
        """ city_id is stored as a string """
        new = self.value(city_id="0001")
        self.assertEqual(type(new.city_id), str)

    def test_user_id(self):
        """ user_id is stored as a string """
        new = self.value(user_id="0001")
        self.assertEqual(type(new.user_id), str)

    def test_name(self):
        """ name is stored as a string """
        new = self.value(name="Lovely place")
        self.assertEqual(type(new.name), str)

    def test_description(self):
        """ description is stored as a string """
        new = self.value(description="Near the beach")
        self.assertEqual(type(new.description), str)

    def test_number_rooms(self):
        """ number_rooms is stored as an int """
        new = self.value(number_rooms=3)
        self.assertEqual(type(new.number_rooms), int)

    def test_number_bathrooms(self):
        """ number_bathrooms is stored as an int """
        new = self.value(number_bathrooms=1)
        self.assertEqual(type(new.number_bathrooms), int)

    def test_max_guest(self):
        """ max_guest is stored as an int """
        new = self.value(max_guest=6)
        self.assertEqual(type(new.max_guest), int)

    def test_price_by_night(self):
        """ price_by_night is stored as an int """
        new = self.value(price_by_night=120)
        self.assertEqual(type(new.price_by_night), int)

    def test_latitude(self):
        """ latitude is stored as a float """
        new = self.value(latitude=37.773972)
        self.assertEqual(type(new.latitude), float)

    def test_longitude(self):
        """ longitude is stored as a float """
        new = self.value(longitude=-122.431297)
        self.assertEqual(type(new.longitude), float)

    def test_amenity_ids(self):
        """ amenity_ids is a list """
        new = self.value()
        self.assertEqual(type(new.amenity_ids), list)

    def test_tablename(self):
        """ Place is mapped to the places table """
        self.assertEqual(Place.__tablename__, 'places')

    def test_numeric_defaults(self):
        """ The integer columns default to 0 """
        columns = Place.__table__.c
        for name in ('number_rooms', 'number_bathrooms',
                     'max_guest', 'price_by_night'):
            with self.subTest(column=name):
                self.assertEqual(columns[name].default.arg, 0)

    def test_nullable_columns(self):
        """ Only description, latitude and longitude can be null """
        columns = Place.__table__.c
        for name in ('description', 'latitude', 'longitude'):
            with self.subTest(column=name):
                self.assertTrue(columns[name].nullable)
        for name in ('city_id', 'user_id', 'name', 'number_rooms'):
            with self.subTest(column=name):
                self.assertFalse(columns[name].nullable)


@unittest.skipIf(os.getenv('HBNB_TYPE_STORAGE') != 'db', 'DBStorage only')
class test_PlaceCascade(unittest.TestCase):
    """ Deleting a User or a City deletes its places """

    def _make_place(self):
        """ Store a State, City, User and Place, and return them """
        state = State(name="California")
        city = City(name="San Francisco", state_id=state.id)
        user = User(email="gui@hbtn.io", password="guipwd")
        place = Place(name="Lovely place", city_id=city.id,
                      user_id=user.id)
        for obj in (state, city, user, place):
            storage.new(obj)
        storage.save()
        return city, user, place

    def test_delete_user_deletes_places(self):
        """ Deleting a User removes its places """
        city, user, place = self._make_place()
        storage.delete(user)
        storage.save()
        self.assertNotIn('Place.' + place.id, storage.all(Place))

    def test_delete_city_deletes_places(self):
        """ Deleting a City removes its places """
        city, user, place = self._make_place()
        storage.delete(city)
        storage.save()
        self.assertNotIn('Place.' + place.id, storage.all(Place))
