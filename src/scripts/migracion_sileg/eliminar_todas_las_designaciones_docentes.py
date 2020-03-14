import sys
import os
import psycopg2

from sileg_model.model.entities.Designation import Designation, DesignationTypes
from sileg_model.model.entities.LeaveLicense import PersonalLeaveLicense, DesignationLeaveLicense
from sileg_model.model.entities.Function import FunctionTypes, Function
from sileg_model.model import open_session
from sileg_model.model.SilegModel import SilegModel
from users.model import open_session as open_users_session
from users.model.UsersModel import UsersModel


if __name__ == '__main__':
    raise Exception('no funciona por las relaciones!!')

    try:
        silegModel = SilegModel()
        with open_session(echo=False) as session:
            try:

                session.query(PersonalLeaveLicense).filter(PersonalLeaveLicense.license_id is not None).delete()
                session.commit()
                session.query(PersonalLeaveLicense).delete()
                session.commit()
                session.query(DesignationLeaveLicense).filter(DesignationLeaveLicense.license_id is not None).delete()
                session.commit()
                session.query(DesignationLeaveLicense).delete()
                session.commit()

                fids = [f.id for f in session.query(Function.id).filter(Function.type == FunctionTypes.DOCENTE).all()]
                dids_doc = session.query(Designation.id).filter(Designation.type == DesignationTypes.PROMOTION, Designation.function_id.in_(fids)).all()
                for did in dids_doc:
                    session.query(Designation).filter(Designation.designation_id == did).delete()
                    session.commit()
                session.query(Designation).filter(Designation.id.in_(did)).delete()
                session.commit()

            except Exception as e:
                print(e)

    except Exception as e2:
        print(e2)