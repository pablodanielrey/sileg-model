"""
    agrupa las materias en deptos como está dado en la base vieja del sileg.
"""

import sys
import psycopg2
import uuid
import json

import logging
from sileg_model.model import open_session
from sileg_model.model.SilegModel import SilegModel
from sileg_model.model.entities.Place import PlaceTypes, Place

def _buscar_lugar_o_crear(session, name):
    pl = session.query(Place).filter(Place.name == name).one_or_none()
    if not pl:
        pid = str(uuid.uuid4())
        p = Place()
        p.id = pid
        p.name = name
        p.parent_id = None
        session.add(p)
        session.commit()
        return _buscar_lugar_o_crear(session, name)
    return pl


if __name__ == '__main__':

    dsn = sys.argv[1]
    depto_materia = []
    con = psycopg2.connect(dsn=dsn)
    try:
        cur = con.cursor()
        try:
            cur.execute("select m.materia_nombre || ' - ' || c.catedra_nombre  as nombre, m.materia_dpto_id from catedras_x_materia cm left join materia m on (m.materia_id = cm.catxmat_materia_id) left join catedra c on (cm.catxmat_catedra_id = c.catedra_id)")
            for c in cur.fetchall():
                d = {
                    'nombre': c[0],
                    'nombre_depto': f"Departamento {c[1]}"
                }
                print(json.dumps(d))
                depto_materia.append(d)
        except Exception as e:
            logging.exception(e)
    except Exception as e1:
        logging.exception(e1)
    
    with open_session() as session:

        """ busco el lugar raiz """
        rn = 'Académica'
        root = _buscar_lugar_o_crear(session, rn)

        for d in depto_materia:
            depto = _buscar_lugar_o_crear(session, d['nombre_depto'])
            depto.type = PlaceTypes.DEPARTAMENTO
            depto.parent_id = root.id

            materia = _buscar_lugar_o_crear(session, d['nombre'])
            materia.type = PlaceTypes.CATEDRA
            materia.parent_id = depto.id

            session.commit()
