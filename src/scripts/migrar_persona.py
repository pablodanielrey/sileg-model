import sys
import psycopg2

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)


from sqlalchemy import event

from sileg_model.model.entities.Function import Function, FunctionTypes
from sileg_model.model.entities.Designation import DesignationEndTypes, DesignationTypes, DesignationStatus, Designation
from sileg_model.model import open_session
from sileg_model.model.SilegModel import SilegModel
from users.model import open_session as open_users_session
from users.model.UsersModel import UsersModel

import uuid

"""
@event.listens_for(Session, 'after_transaction_create')
def _pts(s, t):
    print('transacción iniciada')

@event.listens_for(Session, 'after_transaction_end')
def _pte(s, t):
    print('transacción finalizada')
"""

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

dnis = []

dni = sys.argv[1]
dsn = sys.argv[2]


print('leyendo dnis')
con = psycopg2.connect(dsn=dsn)
try:
    cur = con.cursor()
    try:
        cur.execute('select pers_nrodoc from empleado e left join persona p on (p.pers_id = e.empleado_pers_id)')
        dnis = [str(d[0]) for d in cur]
    finally:
        cur.close()
finally:
    con.close()

def cargar_lugares_y_catedras(cur, functions):
    """ carga dentro del cargo, la catedra y lugar de trbaajo asociados """
    for f in functions:
        if f['cxm']:
            cxmid = f['cxm']
            cur.execute("select m.materia_nombre || ' - ' || c.catedra_nombre  as nombre from catedras_x_materia cm left join materia m on (m.materia_id = cm.catxmat_materia_id) left join catedra c on (cm.catxmat_catedra_id = c.catedra_id) where catxmat_id = %s", (cxmid,))
            f['catedra'] = cur.fetchone()[0]
        if f['lugar_id']:
            lid = f['lugar_id']
            cur.execute("select lugdetrab_nombre from lugar_de_trabajo where lugdetrab_id = %s", (lid,))
            f['lugar'] = cur.fetchone()[0]

def cargar_desig_orginales(cur, empleado_id, functions):
    """ obtengo las designaciones originales para esa persona en cátedras """

    cur.execute("""select desig_id, tipodedicacion_nombre, tipocaracter_nombre, tipocargo_nombre, dd.desig_catxmat_id, dd.desig_fecha_desde, dd.desig_fecha_hasta, 
                r.resolucion_numero, r.resolucion_expediente, r.resolucion_corresponde,
                dd.desig_fecha_baja, r2.resolucion_numero, r2.resolucion_expediente, r2.resolucion_corresponde, tb.tipobajadesig_nombre,
                dd.desig_lugdetrab_id 
                from designacion_docente dd 
                left join resolucion r on (dd.desig_resolucionalta_id = r.resolucion_id)
                left join resolucion r2 on (dd.desig_resolucionbaja_id = r2.resolucion_id)
                left join tipo_baja tb on (dd.desig_tipobaja_id = tb.tipobajadesig_id)
                left join tipo_dedicacion td on (dd.desig_tipodedicacion_id = td.tipodedicacion_id) 
                left join tipo_caracter tc on (dd.desig_tipocaracter_id = tc.tipocaracter_id) 
                left join tipo_cargo tcc on (dd.desig_tipocargo_id = tcc.tipocargo_id) where dd.desig_empleado_id = %s""", (empleado_id,))
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
            'exp':p[8],
            'cor':p[9],
            'fecha_baja': p[10],
            'res_baja': p[11],
            'exp_baja': p[12],
            'cor_baja': p[13],
            'baja_comments': p[14],
            'lugar_id':p[15]
        })

def cargar_prorrogas(cur, did, fs):
    cur.execute("""select prorroga_fecha_desde, prorroga_fecha_hasta, 
                r.resolucion_numero, r.resolucion_expediente, r.resolucion_corresponde,
                r2.resolucion_numero, r2.resolucion_expediente, r2.resolucion_corresponde,
                prorroga_fecha_baja, tb.tipobajadesig_id 
                from prorroga p
                left join resolucion r on (p.prorroga_resolucionalta_id = r.resolucion_id)
                left join resolucion r2 on (p.prorroga_resolucionbaja_id = r2.resolucion_id)
                left join tipo_baja tb on (p.prorroga_tipobaja_id = tb.tipobajadesig_id)
                where prorroga_prorroga_de_id = %s""", (did,))
    for p in cur.fetchall():
        fs.append({
            'desde': p[0],
            'hasta': p[1],
            'res': p[2],
            'exp': p[3],
            'cor': p[4],
            'res_baja': p[5],
            'exp_baja': p[6],
            'cor_baja': p[7],
            'fecha_baja': p[8],
            'baja_comments': p[9]
        })

def cargar_extensiones(cur, did, fs):
    cur.execute("""select extension_id, tipodedicacion_nombre, dd.extension_catxmat_id, dd.extension_fecha_desde, dd.extension_fecha_hasta, 
                r.resolucion_numero, r.resolucion_expediente, r.resolucion_corresponde,
                r2.resolucion_numero, r2.resolucion_expediente, r2.resolucion_corresponde,                            
                dd.extension_fecha_baja, tb.tipobajadesig_nombre,
                dd.extension_lugdetrab_id 
                from extension dd 
                left join resolucion r on (dd.extension_resolucionalta_id = r.resolucion_id)
                left join resolucion r2 on (dd.extension_resolucionbaja_id = r2.resolucion_id)
                left join tipo_baja tb on (dd.extension_tipobaja_id = tb.tipobajadesig_id)
                left join tipo_dedicacion td on (dd.extension_nuevadedicacion_id = td.tipodedicacion_id) 
                where dd.extension_catxmat_id is not null and dd.extension_designacion_id = %s""", (did,))
    for p in cur.fetchall():
        eid = p[0]
        extension_ = {
            'eid': eid,
            'funcion': transform_name_to_new_model(p[1], f['caracter_original'], f['cargo_original']),
            'cxm': p[2],
            'desde': p[3],
            'hasta': p[4],
            'res':p[5],
            'exp':p[6],
            'cor':p[7],
            'res_baja': p[8],
            'exp_baja': p[9],
            'cor_baja': p[10],
            'fecha_baja': p[11],
            'baja_comments': p[12],
            'lugar_id': p[13],
            'prorrogas': []
        }
        fs.append(extension_)


def generar_cargo_original(cur, uid, fid, desig):
    raise Exception('falta terminar')
    """ genero el cargo y lo guardo en el modelo """
    designacion_id = str(uuid.uuid4())
    d = Designation()
    d.id = designacion_id
    d.function_id = fid
    d.user_id = uid
    d.type = DesignationTypes.ORIGINAL
    d.status = DesignationStatus.IMPORTED
    d.res = desig['res']
    d.exp = desig['exp']
    d.cor = desig['cor']
    d.start = desig['desde']
    d.end = desig['hasta']
    d.end_type = DesignationEndTypes.INDETERMINATE
    d.place_id = c
    d.historic = True if p['fecha_baja'] else False
    session.add(d)

def generar_prorrogas(cur, uid, did, prorrogas):
    raise Exception('falta terminar')


with open('miracion-cargos-sileg.csv','w') as archivo:

    for dni in dnis:
        print(dni)
        con = psycopg2.connect(dsn=dsn)
        try:
            cur = con.cursor()
            try:
                cur.execute('select empleado_id from empleado e left join persona p on (p.pers_id = e.empleado_pers_id) where pers_nrodoc = %s', (dni,))
                empleado_id = cur.fetchone()[0]
                cargar_desig_orginales(cur, empleado_id, functions)
                cargar_lugares_y_catedras(cur, functions)
                
                for f in functions:
                    #cargo la info de las prorrogas.
                    did = f['did']
                    f['prorrogas'] = []
                    cargar_prorrogas(cur, did, f['prorrogas'])

                    # cargo la info de las extensiones de cada cargo.
                    f['extensiones'] = []
                    cargar_extensiones(cur, did, f['extensiones'])
                    cargar_lugares_y_catedras(cur, f['extensiones'])
                    for e in f['extensiones']:
                        #cargo la info de las prorrogas de extensión
                        eid = e['eid']
                        cargar_prorrogas(cur, eid, e['prorrogas'])

            finally:
                cur.close()
        finally:
            con.close()


        print('buscando usuario')
        with open_users_session() as s2:
            uid = UsersModel.get_uid_person_number(s2, dni)
            if not uid:
                archivo.write(f'{dni}; No se encuentra un usuario con ese dni\n')
                raise Exception(f'no se encuentra uid para el dni {dni}')

        print('generando')
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
            except Exception as e:
                archivo.write(f"{dni};No se pudieron eliminar las designaciones")
                continue

            try:
                for p in functions:

                    fs = silegModel.get_functions_by_name(session, p['funcion'])
                    if not fs or len(fs) <= 0:
                        archivo.write(f"{dni};No se encuentra la función;{p['funcion']}\n")
                        raise Exception(f"No se encuentra la fucion {p['funcion']}")
                    func = fs[0]

                    c = None
                    if 'catedra' in p and p['catedra']:
                        cs = silegModel.get_places_by_name(session, p['catedra'])
                        if not cs or len(cs) <= 0:
                            archivo.write(f"{dni};No se encuentra la cátedra;{p['catedra']}\n")
                            raise Exception(f"No se encuentra el lugar {p['catedra']}")
                        c = cs[0]
                    
                    if 'lugar' in p and p['lugar']:
                        cs = silegModel.get_places_by_name(session, p['lugar'])
                        if not cs or len(cs) <= 0:
                            archivo.write(f"{dni};No se encuentra el lugar;{p['lugar']}\n")
                            raise Exception(f"No se encuentra el lugar {p['lugar']}")
                        c = cs[0]

                    if not c:
                        raise Exception(f'No se encuentra lugar de trabajo para {uid} {dni}')

                    print(f"usuario {uid} funcion {func} lugar {c}")

                    """ genero el cargo y lo guardo en el modelo """
                    print(f"Generando cargo {func}")
                    designacion_id = str(uuid.uuid4())
                    d = Designation()
                    d.id = designacion_id
                    d.type = DesignationTypes.ORIGINAL
                    d.res = p['res']
                    d.exp = p['exp']
                    d.cor = p['cor']
                    d.start = p['desde']
                    d.end = p['hasta']
                    d.end_type = DesignationEndTypes.INDETERMINATE
                    d.function_id = func
                    d.user_id = uid
                    d.place_id = c
                    d.historic = True if p['fecha_baja'] else False
                    session.add(d)
                    session.commit()

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
                        db.exp = p['exp_baja']
                        db.cor = p['cor_baja']
                        db.comments = p['baja_comments']
                        session.add(db)
                        session.commit()

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
                        session.commit()

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
                            session.commit()


                    """ genero las extensiones y las almaceno dentro del modelo """
                    for pp in p['extensiones']:

                        """ busco el cargo """
                        fs = silegModel.get_functions_by_name(session, pp['funcion'])
                        if not fs or len(fs) <= 0:
                            archivo.write(f"{dni};No se encuentra la función;{pp['funcion']}")
                            raise Exception(f"No se encuentra la fucion {pp['funcion']}")
                        funcex = fs[0]

                        """ busco el lugar """
                        cs = silegModel.get_places_by_name(session, pp['catedra'])
                        if not cs or len(cs) <= 0:
                            archivo.write(f"{dni};No se encuentra la cátedra;{pp['catedra']}\n")
                            raise Exception(f"No se encuentra el lugar {pp['catedra']}\n")
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
                        session.commit()

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
                            session.commit()

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
                            session.commit()                    

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
                                session.commit()
                
                    session.commit()
                    if 'catedra' in p:
                        archivo.write(f"{dni};{p['funcion']};{p['catedra']};correctamente migrado\n")
                    if 'lugar' in p:
                        archivo.write(f"{dni};{p['funcion']};{p['lugar']};correctamente migrado\n")

            except Exception as e:
                archivo.write(f"{dni};{e}\n")
                logging.exception(e)

        archivo.flush()
