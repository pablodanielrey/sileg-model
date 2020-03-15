"""
    Tipos de designaciones:
        ORIGINAL = cargo de planta docente principal
        EXTENSION = extensión del período - es una PRORROGA de una designación ORIGINAL
        PROMOTION = extensión del cargo - es una EXTENSION de una designación ORIGINAL
        REPLACEMENT = suplencia de una designación
        DISCHARGE = baja de una designación
        FUNCTION = formalmente cumplimiento de funciones
        RELATED_FUNCTION = informalmente marca el cumplimiento de una función asociada a un cargo (reemplaza a las anotaciones)

"""


from sqlalchemy import Column, String, Date, Table, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship, backref

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
    RELATED_FUNCTION = 'RELATED_FUNCTION'
    FUNCTION = 'FUNCTION'


class DesignationStatus(Enum):
    PENDING = 'PENDING'
    APROVED = 'APROVED'
    EFFECTIVE = 'EFFECTIVE'
    IMPORTED = 'IMPORTED'


class Designation(Base):

    __tablename__ = 'designations'

    start = Column(Date)
    end = Column(Date)
    end_type = Column(SQLEnum(DesignationEndTypes))
    
    historic = Column(Boolean, default=False)

    exp = Column(String)
    res = Column(String)
    cor = Column(String)

    status = Column(SQLEnum(DesignationStatus))

    type = Column(SQLEnum(DesignationTypes))

    labels = relationship('DesignationLabel', cascade="all, delete")

    """ solo para las designaciones docentes. hay que analizar si esta correcto hacerlo aca """
    convalidation = relationship('DesignationConvalidation', cascade="all, delete")
    adjusted = relationship('DesignationAdjusted', cascade="all, delete")

    designation_id = Column(String, ForeignKey('designations.id'))

    user_id = Column(String)

    function_id = Column(String, ForeignKey('functions.id'))
    function = relationship('Function', back_populates='designations')

    place_id = Column(String, ForeignKey('places.id'))
    place = relationship('Place', back_populates='designations')

    comments = Column(String)


Designation.designations = relationship('Designation', backref=backref('designation', remote_side=[Designation.id]))
Function.designations = relationship('Designation', back_populates='function')
Place.designations = relationship('Designation', back_populates='place')


class DesignationConvalidation(Base):

    __tablename__ = 'designation_convalidations'

    designation_id = Column(String, ForeignKey('designations.id'))
    convalidation = Column(Date)
    

class DesignationAdjusted(Base):

    __tablename__ = 'designation_adjusts'

    designation_id = Column(String, ForeignKey('designations.id'))
    start = Column(Date)
    end = Column(Date)
    exp = Column(String)
    res = Column(String)
    cor = Column(String)

class DesignationLabel(Base):

    __tablename__ = 'designation_labels'

    designation_id = Column(String, ForeignKey('designations.id'))
    name = Column(String)
    value = Column(String)
