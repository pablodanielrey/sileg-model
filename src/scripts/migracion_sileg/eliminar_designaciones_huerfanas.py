
import sys
import psycopg2
import uuid
import json

import logging
from sileg_model.model import open_session
from sileg_model.model.SilegModel import SilegModel
from sileg_model.model.entities.Place import PlaceTypes, Place
from sileg_model.model.entities.Designation import Designation

if __name__ == '__main__':

    with open_session() as session:
        ds = [d for d in session.query(Designation).filter(Designation.designation_id == None, Designation.user_id == None).all()]
        total = len(ds)
        actual = 0
        for d in ds:
            actual = actual + 1
            print(f"{actual}/{total}")
            session.delete(d)
            session.commit()
