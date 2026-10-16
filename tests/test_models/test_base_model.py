#!/usr/bin/python3
""" Unit tests for BaseModel, shared by every model's test class """
from models.base_model import BaseModel
from models import storage
import unittest
import datetime
from uuid import UUID
import json
import os


class test_basemodel(unittest.TestCase):
    """ Tests for BaseModel; subclassed by every model's test class """

    def __init__(self, *args, **kwargs):
        """ Set the class under test """
        super().__init__(*args, **kwargs)
        self.name = 'BaseModel'
        self.value = BaseModel

    def setUp(self):
        """ Nothing to set up """
        pass

    def tearDown(self):
        """ Remove the storage file """
        try:
            os.remove('file.json')
        except Exception:
            pass

    def test_default(self):
        """ Instance has the right type """
        i = self.value()
        self.assertEqual(type(i), self.value)

    def test_kwargs(self):
        """ An instance rebuilt from to_dict is a new object """
        i = self.value()
        copy = i.to_dict()
        new = BaseModel(**copy)
        self.assertFalse(new is i)

    def test_kwargs_int(self):
        """ Non-string keyword names raise TypeError """
        i = self.value()
        copy = i.to_dict()
        copy.update({1: 2})
        with self.assertRaises(TypeError):
            new = BaseModel(**copy)

    @unittest.skipIf(os.getenv('HBNB_TYPE_STORAGE') == 'db',
                     'FileStorage only')
    def test_save(self):
        """ save writes the instance to the JSON file """
        i = self.value()
        i.save()
        key = self.name + "." + i.id
        with open('file.json', 'r') as f:
            j = json.load(f)
            self.assertEqual(j[key], i.to_dict())

    def test_str(self):
        """ __str__ shows class, id and attributes, without SQLAlchemy """
        i = self.value()
        attributes = {key: value for key, value in i.__dict__.items()
                      if key != '_sa_instance_state'}
        self.assertEqual(str(i), '[{}] ({}) {}'.format(self.name, i.id,
                         attributes))

    def test_todict(self):
        """ to_dict is stable """
        i = self.value()
        n = i.to_dict()
        self.assertEqual(i.to_dict(), n)

    def test_todict_no_sa_state(self):
        """ to_dict never contains _sa_instance_state """
        i = self.value()
        self.assertNotIn('_sa_instance_state', i.to_dict())

    def test_kwargs_none(self):
        """ None as a keyword name raises TypeError """
        n = {None: None}
        with self.assertRaises(TypeError):
            new = self.value(**n)

    def test_kwargs_one(self):
        """ A keyword argument becomes an instance attribute """
        n = {'Name': 'test'}
        new = self.value(**n)
        self.assertEqual(new.Name, 'test')

    def test_id(self):
        """ id is a string """
        new = self.value()
        self.assertEqual(type(new.id), str)

    def test_created_at(self):
        """ created_at is a datetime """
        new = self.value()
        self.assertEqual(type(new.created_at), datetime.datetime)

    def test_updated_at(self):
        """ updated_at is a datetime, distinct from created_at """
        new = self.value()
        self.assertEqual(type(new.updated_at), datetime.datetime)
        n = new.to_dict()
        new = BaseModel(**n)
        self.assertFalse(new.created_at == new.updated_at)

    @unittest.skipIf(os.getenv('HBNB_TYPE_STORAGE') == 'db',
                     'FileStorage only')
    def test_init_does_not_register(self):
        """ Creating an instance does not add it to storage """
        new = self.value()
        self.assertNotIn(self.name + '.' + new.id, storage.all())

    @unittest.skipIf(os.getenv('HBNB_TYPE_STORAGE') == 'db',
                     'FileStorage only')
    def test_delete(self):
        """ delete removes a saved instance from storage """
        new = self.value()
        new.save()
        new.delete()
        self.assertNotIn(self.name + '.' + new.id, storage.all())
