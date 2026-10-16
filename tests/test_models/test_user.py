#!/usr/bin/python3
""" Unit tests for User """
from tests.test_models.test_base_model import test_basemodel
from models.user import User


class test_User(test_basemodel):
    """ Tests for User """

    def __init__(self, *args, **kwargs):
        """ Set the class under test """
        super().__init__(*args, **kwargs)
        self.name = "User"
        self.value = User

    def test_first_name(self):
        """ first_name is stored as a string """
        new = self.value(first_name="Guillaume")
        self.assertEqual(type(new.first_name), str)

    def test_last_name(self):
        """ last_name is stored as a string """
        new = self.value(last_name="Snow")
        self.assertEqual(type(new.last_name), str)

    def test_email(self):
        """ email is stored as a string """
        new = self.value(email="gui@hbtn.io")
        self.assertEqual(type(new.email), str)

    def test_password(self):
        """ password is stored as a string """
        new = self.value(password="guipwd")
        self.assertEqual(type(new.password), str)

    def test_names_optional(self):
        """ first_name and last_name are optional (None until set) """
        new = self.value(email="gui@hbtn.io", password="guipwd")
        self.assertIsNone(new.first_name)
        self.assertIsNone(new.last_name)

    def test_tablename(self):
        """ User is mapped to the users table """
        self.assertEqual(User.__tablename__, 'users')
