#!/usr/bin/python3
""" Unit tests for Review """
from tests.test_models.test_base_model import test_basemodel
from models import storage
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User
import os
import unittest


class test_review(test_basemodel):
    """ Tests for Review """

    def __init__(self, *args, **kwargs):
        """ Set the class under test """
        super().__init__(*args, **kwargs)
        self.name = "Review"
        self.value = Review

    def test_place_id(self):
        """ place_id is stored as a string """
        new = self.value(place_id="0001")
        self.assertEqual(type(new.place_id), str)

    def test_user_id(self):
        """ user_id is stored as a string """
        new = self.value(user_id="0001")
        self.assertEqual(type(new.user_id), str)

    def test_text(self):
        """ text is stored as a string """
        new = self.value(text="Amazing place")
        self.assertEqual(type(new.text), str)

    def test_tablename(self):
        """ Review is mapped to the reviews table """
        self.assertEqual(Review.__tablename__, 'reviews')

    def test_not_nullable(self):
        """ text, place_id and user_id cannot be null """
        columns = Review.__table__.c
        for name in ('text', 'place_id', 'user_id'):
            with self.subTest(column=name):
                self.assertFalse(columns[name].nullable)

    def test_foreign_keys(self):
        """ place_id and user_id point to places.id and users.id """
        columns = Review.__table__.c
        places = {fk.target_fullname
                  for fk in columns['place_id'].foreign_keys}
        users = {fk.target_fullname
                 for fk in columns['user_id'].foreign_keys}
        self.assertEqual(places, {'places.id'})
        self.assertEqual(users, {'users.id'})


@unittest.skipIf(os.getenv('HBNB_TYPE_STORAGE') == 'db', 'FileStorage only')
class test_PlaceReviewsFile(unittest.TestCase):
    """ Place.reviews getter with FileStorage """

    def test_reviews_getter(self):
        """ place.reviews returns only the reviews of that place """
        place = Place(name="A")
        other = Place(name="B")
        mine = Review(text="x", place_id=place.id, user_id="u")
        theirs = Review(text="y", place_id=other.id, user_id="u")
        for obj in (place, other, mine, theirs):
            storage.new(obj)
            key = type(obj).__name__ + '.' + obj.id
            self.addCleanup(storage.all().pop, key, None)
        self.assertEqual(place.reviews, [mine])

    def test_reviews_empty(self):
        """ A place without reviews gives an empty list """
        place = Place(name="A")
        self.assertEqual(place.reviews, [])


@unittest.skipIf(os.getenv('HBNB_TYPE_STORAGE') != 'db', 'DBStorage only')
class test_ReviewCascade(unittest.TestCase):
    """ Deleting a User or a Place deletes its reviews """

    def _make_review(self):
        """ Store a State, City, User, Place and Review, return them """
        state = State(name="California")
        city = City(name="San Francisco", state_id=state.id)
        user = User(email="bob@hbtn.io", password="bobpwd")
        place = Place(name="Lovely place", city_id=city.id,
                      user_id=user.id)
        review = Review(text="Amazing place", place_id=place.id,
                        user_id=user.id)
        for obj in (state, city, user, place, review):
            storage.new(obj)
        storage.save()
        return user, place, review

    def test_delete_user_deletes_reviews(self):
        """ Deleting a User removes its reviews """
        user, place, review = self._make_review()
        storage.delete(user)
        storage.save()
        self.assertNotIn('Review.' + review.id, storage.all(Review))

    def test_delete_place_deletes_reviews(self):
        """ Deleting a Place removes its reviews """
        user, place, review = self._make_review()
        storage.delete(place)
        storage.save()
        self.assertNotIn('Review.' + review.id, storage.all(Review))
        storage.delete(user)
        storage.save()
