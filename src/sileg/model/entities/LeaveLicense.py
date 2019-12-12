from sqlalchemy import Column, String, Date, Table, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from . import Base

class PersonalLeaveLicense(Base):

    __tablename__ = 'personal_leave_licenses'

    user_id = Column(String)

    start = Column(Date)
    end = Column(Date)

    historic = Boolean

    exp = Column(String)
    res = Column(String)
    cor = Column(String)

    type = Column(String)

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