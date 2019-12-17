
from .entities.Function import Function, FunctionTypes
from .entities.Designation import Designation

class SilegModel:

    def get_functions(self, session):
        return session.query(Function).all()

    def get_designations(self, session, dids=[]):
        return session.query(Designation).filter(Designation.id in dids).all()

    def get_designations_by_uuid(self, session, uid):
        return session.query(Designation.id).filter(Designation.user_id).all()