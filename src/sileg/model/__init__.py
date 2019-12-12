import os
import contextlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

port = os.environ.get('SILEG_DB_PORT', '5432')

@contextlib.contextmanager
def get_session(echo=False):
    engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(
        os.environ['SILEG_DB_USER'],
        os.environ['SILEG_DB_PASSWORD'],
        os.environ['SILEG_DB_HOST'],
        port,
        os.environ['SILEG_DB_NAME']
    ), echo=echo)

    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()

from .entities import Base
from .SilegModel import SilegModel

__all__ = [
    'SilegModel'
]

def create_tables():

    from .entities.Function import Function
    from .entities.Place import Place
    from .entities.Designation import Designation


    engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(
        os.environ['SILEG_DB_USER'],
        os.environ['SILEG_DB_PASSWORD'],
        os.environ['SILEG_DB_HOST'],
        port,
        os.environ['SILEG_DB_NAME']
    ), echo=True)
    Base.metadata.create_all(engine)
