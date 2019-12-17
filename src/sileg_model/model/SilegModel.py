
from .entities.Function import Function, FunctionTypes
from .entities.Designation import Designation
from .entities.Place import PlaceTypes, Place

class SilegModel:

    def get_functions(self, session):
        return session.query(Function).all()

    def get_designations(self, session, dids=[]):
        return session.query(Designation).filter(Designation.id.in_(dids)).all()

    def get_designations_by_uuid(self, session, uid):
        return [d.id for d in session.query(Designation.id).filter(Designation.user_id == uid).all()]

    def get_places(self, session, pids=[]):
        print(pids)
        return session.query(Place).filter(Place.id.in_(pids)).all()

    def get_all_places(self, session):
        return [p.id for p in session.query(Place.id).all()]