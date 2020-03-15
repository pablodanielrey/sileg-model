
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

    not_remove = [
        '06b1159e-8a83-4e4e-b8af-a8ad3dd47258',
        '8b679c01-d9f9-4a15-ad48-68eab27910fd',
        '2d14c2ce-7a8c-45dc-8aab-3eeff0f2aa2c',
        '387af5e1-f281-4aba-9454-1d5cbbb1f5c7'
    ]

    with open_session() as session:
        places_w_d = [p.place_id for p in session.query(Designation.place_id).group_by(Designation.place_id).all()]
        places = [p.id for p in session.query(Place.id).all()]
        to_remove = [p for p in places if p not in places_w_d]

    for p in to_remove:
        if p in not_remove:
            continue
        with open_session() as session:
            try:
                print(f"eliminando {p}")
                session.query(Place).filter(Place.id == p).delete()
                session.commit()
            except Exception as e:
                logging.exception(e)