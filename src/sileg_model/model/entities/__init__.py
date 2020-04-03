
import uuid
import os
from sqlalchemy import create_engine
from sqlalchemy import Column, String, DateTime, func, desc
from sqlalchemy.ext.declarative import declarative_base
#from flask_jsontools import JsonSerializableBase
from sqlalchemy_serializer import SerializerMixin

def generateId():
    return str(uuid.uuid4())

class MyBaseClass(SerializerMixin):

    id = Column(String, primary_key=True, default=generateId)
    created = Column(DateTime, server_default=func.now())
    updated = Column(DateTime, onupdate=func.now())
    deleted = Column(DateTime)

#Base = declarative_base(cls=(JsonSerializableBase,MyBaseClass))
Base = declarative_base(cls=MyBaseClass)

