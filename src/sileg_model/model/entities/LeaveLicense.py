from sqlalchemy import Column, String, Date, Table, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship

from enum import Enum

from . import Base

"""
utndocentes-> ;
 tipolicencia_id | tipolicencia_descripcion | tipolicencia_abrev | usuario_log 
-----------------+--------------------------+--------------------+-------------
               2 | Renta Suspendida         | R/S                |            
               3 | Retención de Cargo       | R/C                |            
               4 | Suspension Transitoria   | S/T                |            
               1 | Licencia                 | LIC                |         113
               7 | Art. 46 Inc. C           | Art.46             |          47
"""
class LicenseTypes(Enum):
    INDETERMINATE = 'INDETERMINATE'
    S = 'S'
    RS = 'RS'
    RC = 'RC'
    LIC = 'LIC'
    ST = 'ST'


"""
Esto es lo que se encuentra en la base pero me suena a que es una baja de cargo, no un tipo de fin de licencia!!.

utndocentes=> select  * from tipo_baja;
 tipobajadesig_id |  tipobajadesig_nombre   | usuario_log 
------------------+-------------------------+-------------
                1 | Fallecimiento           |            
                5 | Renuncia                |            
                9 | Término de Designación  |          45
               11 | Cambio de Cátedra       |          45
                7 | Termino de Extensión    |          47
                6 | Limitación de Funciones |          47
               10 | Térrmino de Licencia    |          47
                8 | Cambio de Licencia      |          47
               12 | reintegro de licencia   |         113
               13 | Jubilación              |          99
               14 | Limitacion de Cargo     |         139
(11 rows)
"""
class LicenseEndTypes(Enum):
    INDETERMINATE = 'INDETERMINATE'


class PersonalLeaveLicense(Base):

    __tablename__ = 'personal_leave_licenses'

    user_id = Column(String)

    type = Column(SQLEnum(LicenseTypes))

    start = Column(Date)
    end = Column(Date)
    end_type = Column(SQLEnum(LicenseEndTypes))

    historic = Boolean

    exp = Column(String)
    res = Column(String)
    cor = Column(String)

    comments = Column(String)


class DesignationLeaveLicense(Base):

    __tablename__ = 'designation_leave_licenses'

    designation_id = Column(String, ForeignKey('designations.id'))
    designation = relationship('Designation', foreign_keys=[designation_id])    

    start = Column(Date)
    end = Column(Date)

    historic = Boolean

    exp = Column(String)
    res = Column(String)
    cor = Column(String)

    type = Column(SQLEnum(LicenseTypes))

    comments = Column(String)