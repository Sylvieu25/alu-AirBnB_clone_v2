#!/usr/bin/python3
"""This module instantiates the storage engine chosen by the environment.

HBNB_TYPE_STORAGE=db selects DBStorage (MySQL), anything else selects
FileStorage (JSON file).
"""
from os import getenv

if getenv('HBNB_TYPE_STORAGE') == 'db':
    from models.engine.db_storage import DBStorage
    storage = DBStorage()
else:
    from models.engine.file_storage import FileStorage
    storage = FileStorage()
storage.reload()
