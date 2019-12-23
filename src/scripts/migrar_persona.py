import sys
import psycopg2

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)


def transform_name_to_new_model(d,c,cc):
    func = cc + " - "
    
    if 'completo' in d:
        func = func + "Tiempo Completo" + " - "
    elif 'Semidedicación' in d:
        func = func + "Semi Dedicación" + " - "
    else:
        func = func + d + " - "
    
    func = func + c

    return func    


functions = []

dni = sys.argv[1]
dsn = sys.argv[2]
con = psycopg2.connect(dsn=dsn)
try:
    cur = con.cursor()
    try:
        cur.execute('select empleado_id from empleado e left join persona p on (p.pers_id = e.empleado_id) where pers_nrodoc = %s', (dni,))
        empleado_id = cur.fetchone()[0]

        """ obtengo las designaciones originales para esa persona en cátedras """

        cur.execute("""select desig_id, tipodedicacion_nombre, tipocaracter_nombre, tipocargo_nombre, dd.desig_catxmat_id, dd.desig_fecha_desde, dd.desig_fecha_hasta, dd.desig_resolucionalta_id from designacion_docente dd 
                       left join tipo_dedicacion td on (dd.desig_tipodedicacion_id = td.tipodedicacion_id) 
                       left join tipo_caracter tc on (dd.desig_tipocaracter_id = tc.tipocaracter_id) 
                       left join tipo_cargo tcc on (dd.desig_tipocargo_id = tcc.tipocargo_id) where dd.desig_catxmat_id is not null and dd.desig_empleado_id = %s""", (empleado_id,))
        for p in cur:
            functions.append({
                'dni':dni,
                'did': p[0],
                'funcion': transform_name_to_new_model(p[1], p[2], p[3]),
                'cxm': p[4],
                'desde': p[5],
                'hasta': p[6],
                'res':p[7]
            })
            
        for f in functions:
            # cargo la info del lugar
            cxmid = f['cxm']
            cur.execute("select m.materia_nombre || ' - ' || c.catedra_nombre  as nombre from catedras_x_materia cm left join materia m on (m.materia_id = cm.catxmat_materia_id) left join catedra c on (cm.catxmat_catedra_id = c.catedra_id) where catxmat_id = %s", (cxmid,))
            f['catedra'] = cur.fetchone()[0]

            #cargo la info de las prorrogas.
            did = f['did']
            f['prorrogas'] = []
            cur.execute('select prorroga_fecha_desde, prorroga_fecha_hasta, prorroga_resolucionalta_id from prorroga where prorroga_prorroga_de_id = %s', (did,))
            for p in cur:
                f['prorrogas'].append({
                    'desde': p[0],
                    'hasta': p[1],
                    'res': p[2]
                })


    finally:
        cur.close()
finally:
    con.close()


print(functions)

from sileg_model.model.entities.Function import Function, FunctionTypes
from sileg_model.model.entities.Designation import DesignationEndTypes, DesignationTypes, Designation
from sileg_model.model import open_session
from sileg_model.model.SilegModel import SilegModel
from users.model import open_session as open_users_session
from users.model.UsersModel import UsersModel

import uuid

with open_users_session() as s2:
    uid = UsersModel.get_uid_person_number(s2, dni)
    if not uid:
        raise Exception(f'no se encuentra uid para el dni {dni}')


silegModel = SilegModel()
with open_session() as session:
    try:

        """ elimino todas las designaciones de la persona referenciada """
        desigs = silegModel.get_designations_by_uuid(session, uid)
        ds = silegModel.get_designations(session, desigs)
        for d_ in ds:
            session.delete(d_)
        session.commit()
        ds = None

        for p in functions:

            fs = silegModel.get_functions_by_name(session, p['funcion'])
            if not fs or len(fs) <= 0:
                raise Exception(f"No se encuentra la fucion {p['funcion']}")
            func = fs[0]

            cs = silegModel.get_places_by_name(session, p['catedra'])
            if not cs or len(cs) <= 0:
                raise Exception(f"No se encuentra el lugar {p['catedra']}")
            c = cs[0]

            print(f"usuario {uid} funcion {func} catedra {c}")

            """ genero el cargo y lo guardo en el modelo """
            print(f"Generando cargo {func}")
            did = str(uuid.uuid4())
            d = Designation()
            d.id = did
            d.type = DesignationTypes.ORIGINAL
            d.res = p['res']
            d.start = p['desde']
            d.end = p['hasta']
            d.end_type = DesignationEndTypes.INDETERMINATE
            d.function_id = func
            d.user_id = uid
            d.place_id = c
            session.add(d)
            session.commit()

            """ genero las prorrogas y las almaceno dentro del modelo """
            for pp in p['prorrogas']:
                print(f"Generando prorroga {pp['desde']}")
                dp = Designation()
                dp.id = str(uuid.uuid4())
                dp.type = DesignationTypes.EXTENSION
                dp.user_id = uid
                dp.designation_id = did
                dp.res = pp['res']
                dp.start = pp['desde']
                dp.end = pp['hasta']
                dp.end_type = DesignationEndTypes.INDETERMINATE
                dp.function_id = func
                dp.place_id = c
                session.add(dp)
                session.commit()

    except Exception as e:
        raise e

