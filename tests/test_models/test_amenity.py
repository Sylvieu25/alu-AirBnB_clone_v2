#!/usr/bin/python3
""" Unit tests for Amenity and the Place <> Amenity relationship """
from tests.test_models.test_base_model import test_basemodel
from models import storage
from models.amenity import Amenity
from models.base_model import Base
from models.city import City
from models.place import Place, place_amenity
from models.state import State
from models.user import User
import os
import unittest


class test_Amenity(test_basemodel):
    """ Tests for Amenity """

    def __init__(self, *args, **kwargs):
        """ Set the class under test """
        super().__init__(*args, **kwargs)
        self.name = "Amenity"
        self.value = Amenity

    def test_name2(self):
        """ name is stored as a string """
        new = self.value(name="Wifi")
        self.assertEqual(type(new.name), str)

    def test_tablename(self):
        """ Amenity is mapped to the amenities table """
        self.assertEqual(Amenity.__tablename__, 'amenities')

    def test_name_column(self):
        """ name is a 128 character column that cannot be null """
        column = Amenity.__table__.c['name']
        self.assertFalse(column.nullable)
        self.assertEqual(column.type.length, 128)


class test_PlaceAmenityTable(unittest.TestCase):
    """ The place_amenity association table """

    def test_table_name(self):
        """ The table is called place_amenity """
        self.assertEqual(place_amenity.name, 'place_amenity')

    def test_metadata(self):
        """ The table lives in Base.metadata """
        self.assertIs(place_amenity.metadata, Base.metadata)

    def test_columns(self):
        """ The table has place_id and amenity_id, 60 characters each """
        self.assertEqual({c.name for c in place_amenity.c},
                         {'place_id', 'amenity_id'})
        for column in place_amenity.c:
            with self.subTest(column=column.name):
                self.assertEqual(column.type.length, 60)

    def test_primary_keys(self):
        """ Both columns are primary keys and never null """
        for column in place_amenity.c:
            with self.subTest(column=column.name):
                self.assertTrue(column.primary_key)
                self.assertFalse(column.nullable)

    def test_foreign_keys(self):
        """ The columns point to places.id and amenities.id """
        places = {fk.target_fullname
                  for fk in place_amenity.c['place_id'].foreign_keys}
        amenities = {fk.target_fullname
                     for fk in place_amenity.c['amenity_id'].foreign_keys}
        self.assertEqual(places, {'places.id'})
        self.assertEqual(amenities, {'amenities.id'})


@unittest.skipIf(os.getenv('HBNB_TYPE_STORAGE') == 'db', 'FileStorage only')
class test_PlaceAmenitiesFile(unittest.TestCase):
    """ Place.amenities getter and setter with FileStorage """

    def setUp(self):
        """ Create a Place and two stored Amenity objects """
        self.place = Place(name="A")
        self.wifi = Amenity(name="Wifi")
        self.oven = Amenity(name="Oven")
        for obj in (self.wifi, self.oven):
            storage.new(obj)
            self.addCleanup(storage.all().pop, 'Amenity.' + obj.id, None)

    def test_setter_appends_id(self):
        """ Setting amenities adds the Amenity id to amenity_ids """
        self.place.amenities = self.wifi
        self.assertEqual(self.place.amenity_ids, [self.wifi.id])

    def test_getter_returns_amenities(self):
        """ amenities returns the linked Amenity objects """
        self.place.amenities = self.wifi
        self.place.amenities = self.oven
        self.assertCountEqual(self.place.amenities, [self.wifi, self.oven])

    def test_getter_only_linked(self):
        """ amenities leaves out Amenity objects that are not linked """
        self.place.amenities = self.wifi
        self.assertEqual(self.place.amenities, [self.wifi])

    def test_setter_ignores_other_objects(self):
        """ Anything that is not an Amenity is ignored """
        self.place.amenities = "Wifi"
        self.place.amenities = self.place
        self.place.amenities = None
        self.assertEqual(self.place.amenity_ids, [])

    def test_setter_no_duplicates(self):
        """ Adding the same Amenity twice links it once """
        self.place.amenities = self.wifi
        self.place.amenities = self.wifi
        self.assertEqual(self.place.amenity_ids, [self.wifi.id])

    def test_places_do_not_share_ids(self):
        """ Linking an Amenity to one Place does not change another """
        other = Place(name="B")
        self.place.amenities = self.wifi
        self.assertEqual(other.amenity_ids, [])


@unittest.skipIf(os.getenv('HBNB_TYPE_STORAGE') != 'db', 'DBStorage only')
class test_PlaceAmenitiesDB(unittest.TestCase):
    """ The Many-To-Many link between Place and Amenity in MySQL """

    def _count(self, query, args):
        """ Run a COUNT query with MySQLdb, apart from SQLAlchemy """
        import MySQLdb
        conn = MySQLdb.connect(host=os.getenv('HBNB_MYSQL_HOST'),
                               user=os.getenv('HBNB_MYSQL_USER'),
                               passwd=os.getenv('HBNB_MYSQL_PWD'),
                               db=os.getenv('HBNB_MYSQL_DB'))
        try:
            cursor = conn.cursor()
            cursor.execute(query, args)
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def _links(self, place_id):
        """ Number of place_amenity rows for a place """
        return self._count('SELECT COUNT(*) FROM place_amenity '
                           'WHERE place_id = %s', (place_id,))

    def setUp(self):
        """ Store a State, City, User, Place and two Amenity objects """
        state = State(name="California")
        city = City(name="San Francisco", state_id=state.id)
        user = User(email="john@snow.com", password="johnpwd")
        self.place = Place(name="House 1", city_id=city.id,
                           user_id=user.id)
        self.wifi = Amenity(name="Wifi")
        self.cable = Amenity(name="Cable")
        self.place_id = self.place.id
        self.wifi_id = self.wifi.id
        self.cable_id = self.cable.id
        for obj in (state, city, user, self.place, self.wifi, self.cable):
            storage.new(obj)
        storage.save()

    def test_link_creates_rows(self):
        """ Linking amenities adds one row each to place_amenity """
        before = self._links(self.place_id)
        self.place.amenities.append(self.wifi)
        self.place.amenities.append(self.cable)
        storage.save()
        self.assertEqual(self._links(self.place_id) - before, 2)

    def test_amenity_sees_place(self):
        """ Amenity.place_amenities lists the places linked to it """
        self.place.amenities.append(self.wifi)
        storage.save()
        self.assertIn(self.place, self.wifi.place_amenities)

    def test_delete_place_removes_links(self):
        """ Deleting a Place removes its links but keeps the Amenity """
        self.place.amenities.append(self.wifi)
        storage.save()
        storage.delete(self.place)
        storage.save()
        self.assertEqual(self._links(self.place_id), 0)
        self.assertEqual(self._count('SELECT COUNT(*) FROM amenities '
                                     'WHERE id = %s', (self.wifi_id,)), 1)

    def test_delete_amenity_removes_links(self):
        """ Deleting an Amenity removes its links but keeps the Place """
        self.place.amenities.append(self.wifi)
        self.place.amenities.append(self.cable)
        storage.save()
        storage.delete(self.wifi)
        storage.save()
        self.assertEqual(self._links(self.place_id), 1)
        self.assertEqual(self._count('SELECT COUNT(*) FROM places '
                                     'WHERE id = %s', (self.place_id,)), 1)
