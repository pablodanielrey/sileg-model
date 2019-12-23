from sqlalchemy import Column, String, Date, Table, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship

from enum import Enum

from . import Base

from .Function import Function
from .Place import Place

"""
categoria_designacion_table = Table('categoria_designacion', Base.metadata,
    Column('designacion_id', String, ForeignKey('designacion.id')),
    Column('categoria_id', String, ForeignKey('categoria.id'))
)
"""

"""
class Caracter(Base):
    __tablename__ = 'caracter'
    nombre = Column(String, unique=True)
    old_id = Column(String)
"""

class DesignationEndTypes(Enum):
    INDETERMINATE = 'INDETERMINATE'
    CONVALIDATION = 'CONVALIDATION'
    CONTEST = 'CONTEST'
    RENEWAL = 'RENEWAL'
    ENDDATE = 'ENDDATE'
    REPLACEMENT = 'REPLACEMENT'

class DesignationTypes(Enum):
    ORIGINAL = 'ORIGINAL'
    EXTENSION = 'EXTENSION'
    PROMOTION = 'PROMOTION'
    REPLACEMENT = 'REPLACEMENT'
    DISCHARGE = 'DISCHARGE'
    

class Designation(Base):

    __tablename__ = 'designations'

    start = Column(Date)
    end = Column(Date)
    end_type = Column(SQLEnum(DesignationEndTypes))
    
    historic = Column(Boolean)

    exp = Column(String)
    res = Column(String)
    cor = Column(String)

    type = Column(SQLEnum(DesignationTypes))
    #categorias = relationship('CategoriaDesignacion', secondary=categoria_designacion_table, back_populates='designaciones')

    designation_id = Column(String, ForeignKey('designations.id'))
    designations = relationship('Designation', foreign_keys=[designation_id])

    user_id = Column(String)

    function_id = Column(String, ForeignKey('functions.id'))
    function = relationship('Function', back_populates='designations')

    place_id = Column(String, ForeignKey('places.id'))
    place = relationship('Place', back_populates='designations')

    #caracter_id = Column(String, ForeignKey('caracter.id'))
    #caracter = relationship('Caracter', back_populates='tipos_caracter')

    comments = Column(String)

    """
    _mapper_args__ = {
        'polymorphic_on':tipo,
        'polymorphic_identity':'designacion'
    }
    """

Function.designations = relationship('Designation', back_populates='function')
Place.designations = relationship('Designation', back_populates='place')

"""
class BajaDesignacion(Designacion):
    __mapper_args__ = {
        'polymorphic_identity':'baja'
    }

class CategoriaDesignacion(Base):

    __tablename__ = 'categoria'

    nombre = Column(String, unique=True)

    designaciones = relationship('Designacion', secondary=categoria_designacion_table, back_populates='categorias')

    old_id = Column(String)

"""
