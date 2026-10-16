#!/usr/bin/python3
"""Unit tests for FileStorage.all(cls) and FileStorage.delete(obj)."""
import os
import unittest

from models.base_model import BaseModel
from models.engine.file_storage import FileStorage
from models.state import State
from models.user import User


@unittest.skipIf(os.getenv('HBNB_TYPE_STORAGE') == 'db',
                 'FileStorage only')
class TestFileStorageAllDelete(unittest.TestCase):
    """Filtering with all(cls) and removing with delete(obj)."""

    def setUp(self):
        """Start every test with empty storage."""
        self.fs = FileStorage()
        self.objects = FileStorage._FileStorage__objects
        self.backup = dict(self.objects)
        self.objects.clear()

    def tearDown(self):
        """Restore storage and remove the JSON file."""
        self.objects.clear()
        self.objects.update(self.backup)
        try:
            os.remove('file.json')
        except OSError:
            pass

    def _add(self, cls):
        """Create an instance of cls, store it and return it."""
        obj = cls()
        self.fs.new(obj)
        return obj

    def test_all_without_cls_returns_storage(self):
        """all() returns the storage dictionary itself."""
        self.assertIs(self.fs.all(), self.objects)

    def test_all_cls_returns_dict(self):
        """all(cls) returns a dictionary."""
        self.assertIsInstance(self.fs.all(State), dict)

    def test_all_cls_empty(self):
        """all(cls) is empty when no object of cls is stored."""
        self._add(User)
        self.assertEqual(self.fs.all(State), {})

    def test_all_cls_filters(self):
        """all(cls) returns only the objects of cls."""
        state = self._add(State)
        user = self._add(User)
        result = self.fs.all(State)
        self.assertIn('State.' + state.id, result)
        self.assertNotIn('User.' + user.id, result)
        self.assertEqual(len(result), 1)

    def test_all_cls_name(self):
        """all(cls) also accepts the class name as a string."""
        state = self._add(State)
        self._add(User)
        self.assertEqual(list(self.fs.all('State')), ['State.' + state.id])

    def test_all_cls_exact_class(self):
        """all(BaseModel) does not return subclass instances."""
        base = self._add(BaseModel)
        self._add(State)
        self.assertEqual(list(self.fs.all(BaseModel)),
                         ['BaseModel.' + base.id])

    def test_all_cls_is_a_copy(self):
        """Changing all(cls) does not change storage."""
        state = self._add(State)
        self.fs.all(State).clear()
        self.assertIn('State.' + state.id, self.fs.all())

    def test_delete_removes_object(self):
        """delete(obj) removes the object from storage."""
        state = self._add(State)
        self.fs.delete(state)
        self.assertNotIn('State.' + state.id, self.fs.all())

    def test_delete_keeps_other_objects(self):
        """delete(obj) leaves every other object in place."""
        first = self._add(State)
        second = self._add(State)
        self.fs.delete(first)
        self.assertIn('State.' + second.id, self.fs.all())

    def test_delete_none(self):
        """delete(None) does nothing."""
        self._add(State)
        before = dict(self.fs.all())
        self.fs.delete(None)
        self.assertEqual(self.fs.all(), before)

    def test_delete_without_argument(self):
        """delete() with no argument does nothing."""
        self._add(State)
        before = dict(self.fs.all())
        self.fs.delete()
        self.assertEqual(self.fs.all(), before)

    def test_delete_object_not_stored(self):
        """Deleting an object that is not stored does nothing."""
        self._add(State)
        outsider = State()
        self.objects.pop('State.' + outsider.id, None)
        before = dict(self.fs.all())
        self.fs.delete(outsider)
        self.assertEqual(self.fs.all(), before)

    def test_delete_then_save(self):
        """A deleted object is gone from the file after save()."""
        state = self._add(State)
        self.fs.save()
        self.fs.delete(state)
        self.fs.save()
        self.objects.clear()
        self.fs.reload()
        self.assertNotIn('State.' + state.id, self.fs.all())
