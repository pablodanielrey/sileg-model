
import sys
import psycopg2
from sileg_model.model import open_session
from sileg_model.model.entities.Function import Function, FunctionTypes
from sileg_model.model.entities.Designation import Designation, DesignationTypes, DesignationEndTypes, DesignationStatus

def _get_cargos(cur):
    cargos = []
    cur.execute("select id, nombre, nivel from cargo where tipo = 'No Docente'")
    for l in cur:
        cargo = {
            'id': l[0],
            'nombre': l[1],
            'nivel': l[2]
        }
        cargos.append(cargo)
    return cargos


def _get_designations(cur, cids=[]):
    designaciones = []
    cur.execute('select id, usuario_id, lugar_id, cargo_id, desde, hasta, historico from designacion where cargo_id in %s', (tuple(cids),))
    for d in cur:
        desig = {
            'id': d[0],
            'usuario_id': d[1],
            'lugar_id': d[2],
            'cargo_id': d[3],
            'desde': d[4],
            'hasta': d[5],
            'historico': d[6]
        }
        designaciones.append(desig)
    return designaciones



if __name__ == '__main__':
    lugares = []
    dsn = sys.argv[1]
    con = psycopg2.connect(dsn=dsn)
    try:
        cur = con.cursor()
        try:
            cargos = _get_cargos(cur)
            cids = [c['id'] for c in cargos]
            designaciones = _get_designations(cur, cids)
        finally:
            cur.close()
    finally:
        con.close()

    for c in cargos:
        with open_session() as session:
            if session.query(Function.id).filter(Function.id == c['id']).count() > 0:
                continue
            f = Function()
            f.id = c['id']
            f.type = FunctionTypes.NODOCENTE
            f.name = c['nombre']
            f.level = c['nivel']
            session.add(f)
            session.commit()

    for l in designaciones:
        try:
            print(f"--- MIGRANDO ---- {l['id']}")
            with open_session() as session:
                if session.query(Designation.id).filter(Designation.id == l['id']).count() > 0:
                    continue
                d = Designation()
                d.id = l['id']
                d.status = DesignationStatus.APROVED
                d.type = DesignationTypes.ORIGINAL
                d.end_type = DesignationEndTypes.INDETERMINATE
                d.start = l['desde']
                d.end = l['hasta']
                d.user_id = l['usuario_id']
                d.function_id = l['cargo_id']
                d.place_id = l['lugar_id']
                session.add(d)
                session.commit()
        except Exception as e:
            print(e)

    