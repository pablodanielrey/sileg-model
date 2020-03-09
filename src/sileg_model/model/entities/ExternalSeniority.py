
from sqlalchemy import Column, String, Integer
from . import Base

class ExternalSeniority(Base):

    __tablename__ = 'external_seniority'

    days = Column(Integer)
    months = Column(Integer)
    years = Column(Integer)

    user_id = Column(String)