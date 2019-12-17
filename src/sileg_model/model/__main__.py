
from sileg_model.model import create_tables
create_tables()

from sileg_model.model import open_session
from sileg_model.model.SilegModel import SilegModel

with open_session() as ss:
    s = SilegModel()
    s._insert_functions(ss)
    ss.commit()