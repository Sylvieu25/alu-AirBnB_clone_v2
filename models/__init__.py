#!/usr/bin/python3
"""This module instantiates the storage engine chosen by the environment.

HBNB_TYPE_STORAGE=db selects DBStorage (MySQL), anything else selects
FileStorage (JSON file). The model classes are imported here so that
"from models import *" gives access to all of them.
"""
from os import getenv

from models.base_model import BaseModel
from models.amenity import Amenity
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User

if getenv('HBNB_TYPE_STORAGE') == 'db':
    from models.engine.db_storage import DBStorage
    storage = DBStorage()
else:
    from models.engine.file_storage import FileStorage
    storage = FileStorage()
storage.reload()
