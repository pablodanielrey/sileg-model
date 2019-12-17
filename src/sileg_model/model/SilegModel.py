
from .entities.Function import Function, FunctionTypes

class SilegModel:

    def get_functions(self, session):
        return session.query(Function).all()
