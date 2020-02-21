from sqlalchemy import Column, String, Enum as SQLEnum

from enum import Enum

from . import Base

class SilegLogTypes(Enum):
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'

class SilegLog(Base):

    __tablename__ = 'sileg_log'

    type = Column(SQLEnum(SilegLogTypes))
    entity_id = Column(String)
    authorizer_id = Column(String)
    data = Column(String)