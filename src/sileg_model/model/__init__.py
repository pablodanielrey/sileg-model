import os
import contextlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@contextlib.contextmanager
def open_session(echo=False):
    engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(
        os.environ['SILEG_DB_USER'],
        os.environ['SILEG_DB_PASSWORD'],
        os.environ['SILEG_DB_HOST'],
        os.environ['SILEG_DB_PORT'],
        os.environ['SILEG_DB_NAME']
    ), echo=echo)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()

