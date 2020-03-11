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
    #categorias = relationship('CategoriaDesignacion', secondary=categoria_designacion_table, back_populates='designaciones')

    designation_id = Column(String, ForeignKey('designations.id'))

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

Designation.designations = relationship('Designation', backref=backref('designation', remote_side=[Designation.id]))
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
