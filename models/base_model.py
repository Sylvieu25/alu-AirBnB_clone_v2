#!/usr/bin/python3
"""This module defines a base class for all models in our hbnb clone"""
import uuid
from datetime import datetime

import models
from sqlalchemy import Column, DateTime, String
try:
    from sqlalchemy.orm import declarative_base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'


class BaseModel:
    """A base class for all hbnb models"""
    id = Column(String(60), primary_key=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, *args, **kwargs):
        """Instantiate a new model.

        A new id and timestamps are always generated, then any kwargs
        are applied on top: values loaded from storage replace the
        generated ones, and extra values (like name) become attributes.
        """
        self.id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        for key, value in kwargs.items():
            if key == '__class__':
                continue
            if key in ('created_at', 'updated_at') and \
                    isinstance(value, str):
                value = datetime.strptime(value, TIME_FORMAT)
            setattr(self, key, value)

    def __str__(self):
        """Returns a string representation of the instance"""
        attributes = {key: value for key, value in self.__dict__.items()
                      if key != '_sa_instance_state'}
        return '[{}] ({}) {}'.format(type(self).__name__, self.id,
                                     attributes)

    def save(self):
        """Update updated_at, then add the instance to storage and save"""
        self.updated_at = datetime.utcnow()
        models.storage.new(self)
        models.storage.save()

    def to_dict(self):
        """Convert instance into dict format"""
        dictionary = dict(self.__dict__)
        dictionary['__class__'] = type(self).__name__
        dictionary['created_at'] = self.created_at.isoformat()
        dictionary['updated_at'] = self.updated_at.isoformat()
        dictionary.pop('_sa_instance_state', None)
        return dictionary

    def delete(self):
        """Delete the current instance from storage"""
        models.storage.delete(self)
