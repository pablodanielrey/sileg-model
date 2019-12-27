import sys
import psycopg2

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)

from sileg_model.model import Session
from sqlalchemy import event

@event.listens_for(Session, 'after_transaction_create')
def _pts(s, t):
    print('transacción iniciada')

@event.listens_for(Session, 'after_transaction_end')
def _pte(s, t):
    print('transacción finalizada')

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
        cur.execute('select empleado_id from empleado e left join persona p on (p.pers_id = e.empleado_pers_id) where pers_nrodoc = %s', (dni,))
        empleado_id = cur.fetchone()[0]

        """ obtengo las designaciones originales para esa persona en cátedras """

        cur.execute("""select desig_id, tipodedicacion_nombre, tipocaracter_nombre, tipocargo_nombre, dd.desig_catxmat_id, dd.desig_fecha_desde, dd.desig_fecha_hasta, dd.desig_resolucionalta_id,
                       dd.desig_fecha_baja, dd.desig_resolucionbaja_id, tb.tipobajadesig_nombre from designacion_docente dd 
                       left join tipo_baja tb on (dd.desig_tipobaja_id = tb.tipobajadesig_id)
                       left join tipo_dedicacion td on (dd.desig_tipodedicacion_id = td.tipodedicacion_id) 
                       left join tipo_caracter tc on (dd.desig_tipocaracter_id = tc.tipocaracter_id) 
                       left join tipo_cargo tcc on (dd.desig_tipocargo_id = tcc.tipocargo_id) where dd.desig_catxmat_id is not null and dd.desig_empleado_id = %s""", (empleado_id,))
        for p in cur.fetchall():
            functions.append({
                'dni':dni,
                'did': p[0],
                'funcion': transform_name_to_new_model(p[1], p[2], p[3]),
                'caracter_original': p[2],
                'cargo_original': p[3],
                'cxm': p[4],
                'desde': p[5],
                'hasta': p[6],
                'res':p[7],
                'fecha_baja': p[8],
                'res_baja': p[9],
                'baja_comments': p[10]
            })
            
        for f in functions:
            # cargo la info del lugar
            cxmid = f['cxm']
            cur.execute("select m.materia_nombre || ' - ' || c.catedra_nombre  as nombre from catedras_x_materia cm left join materia m on (m.materia_id = cm.catxmat_materia_id) left join catedra c on (cm.catxmat_catedra_id = c.catedra_id) where catxmat_id = %s", (cxmid,))
            f['catedra'] = cur.fetchone()[0]

            #cargo la info de las prorrogas.
            did = f['did']
            f['prorrogas'] = []
            cur.execute("""select prorroga_fecha_desde, prorroga_fecha_hasta, prorroga_resolucionalta_id, 
                           prorroga_resolucionbaja_id, prorroga_fecha_baja, tb.tipobajadesig_id 
                           from prorroga p
                           left join tipo_baja tb on (p.prorroga_tipobaja_id = tb.tipobajadesig_id)
                           where prorroga_prorroga_de_id = %s""", (did,))
            for p in cur.fetchall():
                f['prorrogas'].append({
                    'desde': p[0],
                    'hasta': p[1],
                    'res': p[2],
                    'res_baja': p[3],
                    'fecha_baja': p[4],
                    'baja_comments': p[5]
                })

            # cargo la info de las extensiones de cada cargo.
            f['extensiones'] = []
            cur.execute("""select extension_id, tipodedicacion_nombre, dd.extension_catxmat_id, dd.extension_fecha_desde, dd.extension_fecha_hasta, dd.extension_resolucionalta_id,
                        dd.extension_resolucionbaja_id, dd.extension_fecha_baja, tb.tipobajadesig_nombre
                        from extension dd 
                        left join tipo_baja tb on (dd.extension_tipobaja_id = tb.tipobajadesig_id)
                        left join tipo_dedicacion td on (dd.extension_nuevadedicacion_id = td.tipodedicacion_id) 
                        where dd.extension_catxmat_id is not null and dd.extension_designacion_id = %s""", (did,))
            for p in cur.fetchall():
                # cargo la info del lugar
                cxme_ = p[2]
                cxmid = cxme_
                cur.execute("select m.materia_nombre || ' - ' || c.catedra_nombre  as nombre from catedras_x_materia cm left join materia m on (m.materia_id = cm.catxmat_materia_id) left join catedra c on (cm.catxmat_catedra_id = c.catedra_id) where catxmat_id = %s", (cxmid,))
                lugar_extension = cur.fetchone()[0]

                eid = p[0]
                extension_ = {
                    'eid': eid,
                    'funcion': transform_name_to_new_model(p[1], f['caracter_original'], f['cargo_original']),
                    'catedra': lugar_extension,
                    'desde': p[3],
                    'hasta': p[4],
                    'res':p[5],
                    'res_baja': p[6],
                    'fecha_baja': p[7],
                    'baja_comments': p[8],
                    'prorrogas': []
                }

                #cargo la info de las prorrogas de extensión
                cur.execute("""select prorroga_fecha_desde, prorroga_fecha_hasta, prorroga_resolucionalta_id, prorroga_resolucionbaja_id, 
                               prorroga_resolucionbaja_id, prorroga_fecha_baja, tb.tipobajadesig_id 
                               from prorroga p
                               left join tipo_baja tb on (p.prorroga_tipobaja_id = tb.tipobajadesig_id)
                               where prorroga_prorroga_de_id = %s""", (eid,))
                for pe in cur.fetchall():
                    extension_['prorrogas'].append({
                        'desde': pe[0],
                        'hasta': pe[1],
                        'res': pe[2],
                        'res_baja': p[3],
                        'fecha_baja': p[4],
                        'baja_comments': p[5]
                    })

                f['extensiones'].append(extension_)


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
            designacion_id = str(uuid.uuid4())
            d = Designation()
            d.id = designacion_id
            d.type = DesignationTypes.ORIGINAL
            d.res = p['res']
            d.start = p['desde']
            d.end = p['hasta']
            d.end_type = DesignationEndTypes.INDETERMINATE
            d.function_id = func
            d.user_id = uid
            d.place_id = c
            d.historic = True if p['fecha_baja'] else False
            session.add(d)
            #session.commit()

            """ genero la baja en el caso de que tenga """
            if p['fecha_baja']:
                print("Generando baja de designacion")
                db = Designation()
                db.type = DesignationTypes.DISCHARGE
                db.designation_id = designacion_id
                db.user_id = uid
                db.function_id = func
                db.place_id = c
                db.start = p['fecha_baja']
                db.end_type = DesignationEndTypes.INDETERMINATE
                db.res = p['res_baja']
                db.comments = p['baja_comments']
                session.add(db)
                #session.commit()

            """ genero las prorrogas y las almaceno dentro del modelo """
            for pp in p['prorrogas']:
                print(f"Generando prorroga {pp['desde']}")
                prorroga_id = str(uuid.uuid4())
                dp = Designation()
                dp.id = prorroga_id
                dp.type = DesignationTypes.EXTENSION
                dp.user_id = uid
                dp.designation_id = designacion_id
                dp.res = pp['res']
                dp.start = pp['desde']
                dp.end = pp['hasta']
                dp.end_type = DesignationEndTypes.INDETERMINATE
                dp.function_id = func
                dp.place_id = c
                dp.historic = True if pp['fecha_baja'] else False
                session.add(dp)
                #session.commit()

                """ genero la baja de la prorroga en el caso de que tenga """
                if pp['fecha_baja']:
                    print("generando baja de prorroga")
                    db = Designation()
                    db.type = DesignationTypes.DISCHARGE
                    db.designation_id = prorroga_id
                    db.user_id = uid
                    db.function_id = func
                    db.place_id = c
                    db.start = pp['fecha_baja']
                    db.end_type = DesignationEndTypes.INDETERMINATE
                    db.res = pp['res_baja']
                    db.comments = pp['baja_comments']
                    session.add(db)
                    #session.commit()


            """ genero las extensiones y las almaceno dentro del modelo """
            for pp in p['extensiones']:

                """ busco el cargo """
                fs = silegModel.get_functions_by_name(session, pp['funcion'])
                if not fs or len(fs) <= 0:
                    raise Exception(f"No se encuentra la fucion {pp['funcion']}")
                funcex = fs[0]

                """ busco el lugar """
                cs = silegModel.get_places_by_name(session, pp['catedra'])
                if not cs or len(cs) <= 0:
                    raise Exception(f"No se encuentra el lugar {pp['catedra']}")
                cex = cs[0]

                print(f"Generando extension {pp['desde']}")
                extension_id = str(uuid.uuid4())
                dp = Designation()
                dp.id = extension_id
                dp.type = DesignationTypes.PROMOTION
                dp.user_id = uid
                dp.designation_id = designacion_id
                dp.res = pp['res']
                dp.start = pp['desde']
                dp.end = pp['hasta']
                dp.end_type = DesignationEndTypes.INDETERMINATE
                dp.function_id = funcex
                dp.place_id = cex
                dp.historic = True if pp['fecha_baja'] else False
                session.add(dp)
                #session.commit()

                """ genero las bajas de las extensiones """
                if pp['fecha_baja']:
                    print("Generando baja de extension")
                    db = Designation()
                    db.type = DesignationTypes.DISCHARGE
                    db.designation_id = extension_id
                    db.user_id = uid
                    db.function_id = funcex
                    db.place_id = cex                    
                    db.start = pp['fecha_baja']
                    db.end_type = DesignationEndTypes.INDETERMINATE
                    db.res = pp['res_baja']
                    db.comments = pp['baja_comments']
                    session.add(db)
                    #session.commit()

                """ genero las prorrogas de las extensiones """

                for pe in pp['prorrogas']:
                    print(f"Generando prorroga {pp['desde']}")
                    eprorroga_id = str(uuid.uuid4())
                    dpe = Designation()
                    dpe.id = eprorroga_id
                    dpe.type = DesignationTypes.EXTENSION
                    dpe.user_id = uid
                    dpe.designation_id = extension_id
                    dpe.res = pp['res']
                    dpe.start = pp['desde']
                    dpe.end = pp['hasta']
                    dpe.end_type = DesignationEndTypes.INDETERMINATE
                    dpe.function_id = funcex
                    dpe.place_id = cex
                    dpe.historic = True if pe['fecha_baja'] else False
                    session.add(dpe)
                    #session.commit()                    

                    """ genero las bajas de las prorrogas de extension """
                    if pe['fecha_baja']:
                        print(f"Generando baja de prorroga de extension")
                        db = Designation()
                        db.type = DesignationTypes.DISCHARGE
                        db.designation_id = eprorroga_id
                        db.user_id = uid
                        db.function_id = funcex
                        db.place_id = cex                    
                        db.start = pe['fecha_baja']
                        db.end_type = DesignationEndTypes.INDETERMINATE
                        db.res = pe['res_baja']
                        db.comments = pe['baja_comments']
                        session.add(db)
                        #session.commit()
        
            session.commit()


    except Exception as e:
        raise e

