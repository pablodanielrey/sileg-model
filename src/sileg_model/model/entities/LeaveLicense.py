from sqlalchemy import Column, String, Date, Table, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship

from enum import Enum

from . import Base


class LicenseTypes(Enum):
    INDETERMINATE = 'INDETERMINATE'
    S = 'S'
    RS = 'RS'
    RC = 'RC'
    LIC = 'LIC'


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

    type = Column(String)

    comments = Column(String)