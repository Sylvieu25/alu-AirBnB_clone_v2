#!/usr/bin/python3
""" State Module for HBNB project """
from os import getenv

import models
from models.base_model import BaseModel, Base
from models.city import City
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship


class State(BaseModel, Base):
    """ State class """
    __tablename__ = 'states'
    name = Column(String(128), nullable=False)

    if getenv('HBNB_TYPE_STORAGE') == 'db':
        cities = relationship('City', backref='state',
                              cascade='all, delete, delete-orphan')
    else:
        @property
        def cities(self):
            """Return the list of City instances linked to this State"""
            return [city for city in models.storage.all(City).values()
                    if city.state_id == self.id]
