
import sys
import psycopg2
from sileg_model.model import open_session
from sileg_model.model.entities.Place import Place, PlaceTypes

def _get_lugar(cur, lid):
    cur.execute('select id, padre_id, creado, actualizado, nombre from lugar where id = %s', (lid,))
    l = cur.fetchone()
    lugar = {
        'id': l[0],
        'padre_id': l[1],
        'creado': l[2],
        'actualizado': l[3],
        'nombre': l[4]
    }
    return lugar


def _get_sublugares(cur, lid, lugares=[]):
    lugar = _get_lugar(cur, lid)
    lugares.append(lugar)
    cur.execute('select id from lugar where padre_id = %s', (lid,))
    lids = [a['id'] for a in lugares]
    to_visit = [l[0] for l in cur if l[0] not in lids]
    for slid in to_visit:
        _get_sublugares(cur, slid, lugares)


if __name__ == '__main__':
    lugares = []
    dsn = sys.argv[1]
    lid = sys.argv[2]
    con = psycopg2.connect(dsn=dsn)
    try:
        cur = con.cursor()
        try:
            _get_sublugares(cur, lid, lugares)
        finally:
            cur.close()
    finally:
        con.close()

    for l in lugares:
        print(f"--- MIGRANDO ---- {l['nombre']}")
        with open_session() as session:
            if session.query(Place.id).filter(Place.id == l['id']).count() > 0:
                continue
            p = Place()
            p.id = l['id']
            p.parent_id = l['padre_id']
            p.name = l['nombre']
            p.type = PlaceTypes.AREA
            session.add(p)
            session.commit()


    