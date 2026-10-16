#!/usr/bin/python3
"""This module defines the DBStorage engine (MySQL with SQLAlchemy)"""
from os import getenv

from models.amenity import Amenity
from models.base_model import Base
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State
from models.user import User
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

classes = {
    'User': User, 'State': State, 'City': City,
    'Amenity': Amenity, 'Place': Place, 'Review': Review
}


class DBStorage:
    """This class manages storage of hbnb models in a MySQL database"""
    __engine = None
    __session = None

    def __init__(self):
        """Create the engine, linked to the database from the env"""
        self.__engine = create_engine(
            'mysql+mysqldb://{}:{}@{}/{}'.format(
                getenv('HBNB_MYSQL_USER'),
                getenv('HBNB_MYSQL_PWD'),
                getenv('HBNB_MYSQL_HOST'),
                getenv('HBNB_MYSQL_DB')),
            pool_pre_ping=True)
        if getenv('HBNB_ENV') == 'test':
            Base.metadata.drop_all(self.__engine)

    def all(self, cls=None):
        """Return a dictionary of objects, optionally of one class.

        cls can be a class or a class name. Only classes mapped to a
        table (subclasses of Base) are queried.
        """
        if cls is None:
            targets = list(classes.values())
        elif isinstance(cls, str):
            targets = [classes[cls]] if cls in classes else []
        else:
            targets = [cls]

        result = {}
        for target in targets:
            if not (isinstance(target, type) and issubclass(target, Base)):
                continue
            for obj in self.__session.query(target).all():
                result['{}.{}'.format(type(obj).__name__, obj.id)] = obj
        return result

    def new(self, obj):
        """Add the object to the current database session"""
        self.__session.add(obj)

    def save(self):
        """Commit all changes of the current database session"""
        self.__session.commit()

    def delete(self, obj=None):
        """Delete obj from the current database session if not None"""
        if obj is not None:
            self.__session.delete(obj)

    def reload(self):
        """Create all tables and a new thread-safe session"""
        Base.metadata.create_all(self.__engine)
        session_factory = sessionmaker(bind=self.__engine,
                                       expire_on_commit=False)
        self.__session = scoped_session(session_factory)
