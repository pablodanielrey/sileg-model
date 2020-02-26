def create_tables():
    import os
    from sqlalchemy import create_engine
    from .Function import Function
    from .Place import Place
    from .Designation import Designation
    from .LeaveLicense import PersonalLeaveLicense, DesignationLeaveLicense
    from .Log import SilegLog
    from . import Base

    engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(
        os.environ['SILEG_DB_USER'],
        os.environ['SILEG_DB_PASSWORD'],
        os.environ['SILEG_DB_HOST'],
        os.environ['SILEG_DB_PORT'],
        os.environ['SILEG_DB_NAME']
    ), echo=True)
    Base.metadata.create_all(engine)

create_tables()