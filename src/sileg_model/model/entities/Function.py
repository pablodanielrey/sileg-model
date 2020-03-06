from sqlalchemy import Column, String, Numeric, ForeignKey, DateTime, Enum as SQLEnum, Integer
from sqlalchemy.orm import relationship

from enum import Enum

from . import Base

class FunctionTypes(Enum):
    DOCENTE = 'Docente'
    NODOCENTE = 'NoDocente'
    AUTORIDAD = 'Autoridad'
    PRE_GRADO = 'Pre Grado'
    ALUMNO = 'Alumno'

class Function(Base):

    __tablename__ = 'functions'

    name = Column(String)
    type = Column(SQLEnum(FunctionTypes))
    description = Column(String)
    level = Column(Integer)

    """
    __mapper_args__ = {
        'polymorphic_on':tipo,
        'polymorphic_identity':'cargo'
    }
    """



"""


q = session.query(Docente).all() -- select * from cargo where tipo = 'Docente'
q = session.query(Cargo).joined(Tipo).where(Cargo.tipo.equals('Docente'))

q = session.query(Cargo, Tipo).leftouterjoin(Cargo, Cargo.tipo_id == Tipo.id)

q = session.query(Usua)


with obtener_sesion() as session:
    designaciones = session.query(Designacion).filter(Designacion.lugar.nombre == 'Contabilidad')
    for d in designaciones:
        cargos = [ {nombre: d.persona.nombre, cargo: d.cargo.nombre}]

retrun cargons

{
    'contabilidad': {
        'cargos': [
            { nombre: '', cargo: ''},
            { nombre: '', cargo: ''},
            { nombre: '', cargo: ''},
            { nombre: '', cargo: ''},
        ]
    }
}


class Docente(Cargo):

    __mapper_args__ = {
        'polymorphic_identity':'Docente'
    }


class DocentePreuniversitario(Cargo):

    __mapper_args__ = {        
        'polymorphic_identity':'Docente Preuniversitario'
    }


class Definir(Cargo):

    __mapper_args__ = {        
        'polymorphic_identity':'Definir'
    }
    

class NoDocente(Cargo):

    __mapper_args__ = {
        'polymorphic_identity':'No Docente'
    }


class AutoridadSuperior(Cargo):

    __mapper_args__ = {
        'polymorphic_identity':'Autoridad Superior'
    }


class BecaDeInvestigacion(Cargo):

    __mapper_args__ = {
        'polymorphic_identity':'Beca'
    }


class BecaExperienciaLaboral(Cargo):

    __mapper_args__ = {
        'polymorphic_identity':'Beca de Experiencia Laboral'
    }


class ContratoDeObra(Cargo):

    __mapper_args__ = {
        'polymorphic_identity':'Contrato de Obra'
    } 


class CumpleFunciones(NoDocente):

    def __init__(self):
        self.id = '245eae51-28c4-4c6b-9085-354606399666'
        self.nombre = 'Cumple Funciones'
"""