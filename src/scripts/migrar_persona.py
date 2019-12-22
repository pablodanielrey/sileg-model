import sys
import psycopg2

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

from sileg_model.model.entities.Function import Function, FunctionTypes
from sileg_model.model import open_session
from sileg_model.model.SilegModel import SilegModel
from users.model import open_session as open_users_session
from users.model.UsersModel import UsersModel

silegModel = SilegModel()
with open_session() as session:
    try:
        for p in functions:

            UsersModel.

            fs = silegModel.get_functions_by_name(session, p['function'])
            if not fs or len(fs) <= 0:
                raise Exception()

        

    except Exception as e:
        print(e)

"""