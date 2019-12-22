
from .entities.Function import Function, FunctionTypes
from .entities.Designation import Designation, DesignationEndTypes
from .entities.Place import PlaceTypes, Place
from .entities.LeaveLicense import PersonalLeaveLicense, DesignationLeaveLicense

class SilegModel:

    def get_designation_end_types(self):
        return [d.value for d in DesignationEndTypes]


    def get_functions(self, session, fids=[]):
        return session.query(Function).filter(Function.id.in_(fids)).all()

    def get_all_functions(self, session):
        return [f.id for f in session.query(Function.id).all()]

    def get_functions_by_name(self, session, name):
        return [f.id for f in session.query(Function.id).filter(Function.name == name).all()]


    def get_designations(self, session, dids=[]):
        return session.query(Designation).filter(Designation.id.in_(dids)).all()

    def get_designations_by_uuid(self, session, uid):
        return [d.id for d in session.query(Designation.id).filter(Designation.user_id == uid).all()]


    def get_places(self, session, pids=[]):
        return session.query(Place).filter(Place.id.in_(pids)).all()

    def get_all_places(self, session):
        return [p.id for p in session.query(Place.id).all()]

    def get_places_by_name(self, session, name):
        return [p.id for p in session.query(Place.id).filter(Place.name == name).all()]


    def get_user_licenses(self, session, uid):
        return [l.id for l in session.query(PersonalLeaveLicense.id).filter(PersonalLeaveLicense.user_id == uid).all()]

    def get_user_designation_licenses(self, session, uid):
        dids = session.query(Designation.id).filter(Designation.user_id == uid)
        return [l.id for l in session.query(DesignationLeaveLicense.id).filter(DesignationLeaveLicense.designation_id.in_(dids)).all()]

    def get_ulicenses(self, session, lids=[]):
        return session.query(PersonalLeaveLicense).filter(PersonalLeaveLicense.id.in_(lids)).all()

    def get_dlicenses(self, session, lids=[]):
        return session.query(DesignationLeaveLicense).filter(DesignationLeaveLicense.id.in_(lids)).all()