
import sys
import psycopg2
from sileg_model.model import open_session
from sileg_model.model.entities.Function import Function, FunctionTypes
from sileg_model.model.entities.Designation import Designation, DesignationTypes, DesignationEndTypes, DesignationStatus
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
    lugares_organizados = {}
    dsn = sys.argv[1]
    con = psycopg2.connect(dsn=dsn)
    try:
        cur = con.cursor()
        try:
            cargos = _get_cargos(cur)
            cids = [c['id'] for c in cargos]
            designaciones = _get_designations(cur, cids)

            lugares_ids = [d['lugar_id'] for d in designaciones]
            for lid in lugares_ids:
                _get_sublugares(cur, lid, lugares)
            for lugar in lugares:
                lugares_organizados[lugar['id']] = lugar


        finally:
            cur.close()
    finally:
        con.close()


    lugar_raiz_no_docentes = '06b1159e-8a83-4e4e-b8af-a8ad3dd47258'
    lugar_raiz_indeterminado = '06b1159e-8a83-4e4e-b8af-a8ad3dd47258'
    with open_session() as session:
        if session.query(Place.id).filter(Place.id == lugar_raiz_indeterminado).count() <= 0:
            p = Place()
            p.id = lugar_raiz_indeterminado
            p.parent_id = lugar_raiz_no_docentes
            p.name = 'No docentes (indeterminados)'
            p.type = PlaceTypes.AREA
            session.add(p)
            session.commit()

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

    lugares_erroneos = []
    for l in designaciones:
        try:
            print(f"--- MIGRANDO ---- {l['id']}")
            with open_session() as session:
                if session.query(Designation.id).filter(Designation.id == l['id']).count() > 0:
                    continue
                print(f"migrando ")
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
            lugares_erroneos.append(l['lugar_id'])

    if len(lugares_erroneos) > 0:
        for l in designaciones:
            try:
                print(f"--- MIGRANDO ---- {l['id']}")
                with open_session() as session:
                    if session.query(Designation.id).filter(Designation.id == l['id']).count() > 0:
                        continue
                    if l['lugar_id'] not in lugares_erroneos:
                        continue
                    print(f"migrando {lugares_organizados[l['lugar_id']]}")
                    d = Designation()
                    d.id = l['id']
                    d.status = DesignationStatus.APROVED
                    d.type = DesignationTypes.ORIGINAL
                    d.end_type = DesignationEndTypes.INDETERMINATE
                    d.start = l['desde']
                    d.end = l['hasta']
                    d.user_id = l['usuario_id']
                    d.function_id = l['cargo_id']
                    d.place_id = lugar_raiz_indeterminado
                    session.add(d)
                    session.commit()
            except Exception as e:
                print(e)
    