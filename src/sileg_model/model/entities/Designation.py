from sqlalchemy import Column, String, Date, Table, ForeignKey, Boolean
from sqlalchemy.orm import relationship

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

class Designation(Base):

    __tablename__ = 'designations'

    start = Column(Date)
    end = Column(Date)
    historic = Column(Boolean)

    exp = Column(String)
    res = Column(String)
    cor = Column(String)

    type = Column(String)
    #categorias = relationship('CategoriaDesignacion', secondary=categoria_designacion_table, back_populates='designaciones')

    designation_id = Column(String, ForeignKey('designations.id'))
    designation = relationship('Designation', foreign_keys=[designation_id])

    user_id = Column(String)

    function_id = Column(String, ForeignKey('functions.id'))
    function = relationship('Function', back_populates='designations')

    place_id = Column(String, ForeignKey('places.id'))
    place = relationship('Place', back_populates='designations')

    #caracter_id = Column(String, ForeignKey('caracter.id'))
    #caracter = relationship('Caracter', back_populates='tipos_caracter')

    comments = Column(String)

    _types = [
        'Original',
        'Prorroga',
        'Extensión',
        'Baja'
    ]

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
