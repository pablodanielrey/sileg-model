import sys
import psycopg2
import datetime
import json

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))



import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)


from sqlalchemy import event

from sileg_model.model.entities.Place import Place, PlaceTypes
from sileg_model.model.entities.Function import Function, FunctionTypes
from sileg_model.model.entities.Designation import DesignationEndTypes, DesignationTypes, DesignationStatus, Designation, DesignationLabel, DesignationAdjusted, DesignationConvalidation
from sileg_model.model.entities.LeaveLicense import LicenseEndTypes, LicenseTypes, DesignationLeaveLicense, PersonalLeaveLicense
from sileg_model.model import open_session
from sileg_model.model.SilegModel import SilegModel
from users.model import open_session as open_users_session
from users.model.UsersModel import UsersModel
from users.model.entities.User import User, IdentityNumber

import uuid


"""
    /////////////////////////////////////////////////////////////////////////////////

    FUNCIONES AUXILIARES A LAS PRINCIPALES SOBRE SILEG VIEJO

    /////////////////////////////////////////////////////////////////////////////////
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
                dd.desig_lugdetrab_id,
                dd.desig_reempa,
                dd.desig_observaciones,
                dd.desig_convalidado,
                dd.desig_ord_esajust, desig_ord_fdesde, desig_ord_fhasta,
                r3.resolucion_numero, r3.resolucion_expediente, r3.resolucion_corresponde
                from designacion_docente dd 
                left join resolucion r on (dd.desig_resolucionalta_id = r.resolucion_id)
                left join resolucion r2 on (dd.desig_resolucionbaja_id = r2.resolucion_id)
                left join tipo_baja tb on (dd.desig_tipobaja_id = tb.tipobajadesig_id)
                left join tipo_dedicacion td on (dd.desig_tipodedicacion_id = td.tipodedicacion_id) 
                left join tipo_caracter tc on (dd.desig_tipocaracter_id = tc.tipocaracter_id) 
                left join tipo_cargo tcc on (dd.desig_tipocargo_id = tcc.tipocargo_id) 
                left join resolucion r3 on (dd.desig_resolucionord_id = r3.resolucion_id) where dd.desig_empleado_id = %s""", (empleado_id,))

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
            'lugar_id': p[15],
            'reemplazo_de_id': p[16],
            'comentarios': p[17],
            'convalidada': p[18],
            'ord': p[19],
            'ord_desde': p[20],
            'ord_hasta': p[21],
            'ord_res': p[22],
            'ord_exp': p[23],
            'ord_cor': p[24]
        })

def cargar_prorrogas(cur, did, de, fs):
    cur.execute("""select prorroga_fecha_desde, prorroga_fecha_hasta, 
                r.resolucion_numero, r.resolucion_expediente, r.resolucion_corresponde,
                r2.resolucion_numero, r2.resolucion_expediente, r2.resolucion_corresponde,
                prorroga_fecha_baja, tb.tipobajadesig_id,
                prorroga_id
                from prorroga p
                left join resolucion r on (p.prorroga_resolucionalta_id = r.resolucion_id)
                left join resolucion r2 on (p.prorroga_resolucionbaja_id = r2.resolucion_id)
                left join tipo_baja tb on (p.prorroga_tipobaja_id = tb.tipobajadesig_id)
                where prorroga_prorroga_de = %s and prorroga_prorroga_de_id = %s""", (de, did))
    for p in cur.fetchall():
        prorr = {
            'desde': p[0],
            'hasta': p[1],
            'res': p[2],
            'exp': p[3],
            'cor': p[4],
            'res_baja': p[5],
            'exp_baja': p[6],
            'cor_baja': p[7],
            'fecha_baja': p[8],
            'baja_comments': p[9],
            'id': p[10]
        }
        fs.append(prorr)
        cargar_prorrogas(cur, prorr['id'], 'pro', fs)

def cargar_extensiones(cur, did, fs, caracter_original, cargo_original):
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
                where dd.extension_designacion_id = %s""", (did,))
    for p in cur.fetchall():
        eid = p[0]
        extension_ = {
            'eid': eid,
            'funcion': transform_name_to_new_model(p[1], caracter_original, cargo_original),
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

def cargar_licencias_cargo(cur, did, ls=[]):
    cur.execute("""select licencia_id, licencia_fecha_desde, licencia_fecha_hasta, licencia_fecha_baja,
                    la.licart_descripcion, la.licart_congocesueldo,
                    ra.resolucion_numero as res_alta, ra.resolucion_expediente as exp_alta, ra.resolucion_corresponde as cor_alta,
                    rb.resolucion_numero as res_baja, rb.resolucion_expediente as exp_baja, rb.resolucion_corresponde as cor_baja,
                    tb.tipobajadesig_nombre,
                    tc.tipofincargo_nombre,
                    tl.tipolicencia_descripcion, tl.tipolicencia_abrev
    from licencia l 
    left join licencia_articulos la on (la.licart_id = l.licencia_articulo_id) 
    left join resolucion ra on (ra.resolucion_id = l.licencia_resolucionalta_id) 
    left join resolucion rb on (rb.resolucion_id = l.licencia_resolucionbaja_id) 
    left join tipo_baja tb on (tb.tipobajadesig_id = l.licencia_tipobaja_id) 
    left join tipo_fin_cargo tc on (tc.tipofincargo_id = l.licencia_tipofincargo_id) 
    left join tipo_licencia tl on (tl.tipolicencia_id = l.licencia_tipolicencia_id) 
    where l.licencia_designacion_id = %s
    """, (did,))
    for c in cur.fetchall():
        lic = {
            'id': c[0],
            'desde': c[1],
            'hasta': c[2],
            'fecha_baja': c[3],
            'articulo': c[4],
            'goce': c[5],
            'res': c[6],
            'exp': c[7],
            'cor': c[8],
            'res_baja': c[9],
            'exp_baja': c[10],
            'cor_baja': c[11],
            'tipo_baja': c[12],
            'fin_cargo': c[13],
            'tipo_lic': c[14],
            'tipo_lic_corto': c[15],
            'prorrogas': []
        }
        ls.append(lic)
        cargar_prorrogas_de_licencia(cur, lic['id'], lic['prorrogas'])

def cargar_prorrogas_de_licencia(cur, lid, prorrogas=[]):
    cur.execute("""select prorroga_id, prorroga_fecha_desde, prorroga_fecha_hasta, 
        prorroga_fecha_baja, tb.tipobajadesig_nombre,
        ra.resolucion_numero as res_alta, ra.resolucion_expediente as exp_alta, ra.resolucion_corresponde as cor_alta,
        rb.resolucion_numero as res_baja, rb.resolucion_expediente as exp_baja, rb.resolucion_corresponde as cor_baja
        from prorroga p 
        left join resolucion ra on (ra.resolucion_id = p.prorroga_resolucionalta_id) 
        left join resolucion rb on (rb.resolucion_id = p.prorroga_resolucionbaja_id) 
        left join tipo_baja tb on (tb.tipobajadesig_id = p.prorroga_tipobaja_id) 
        where p.prorroga_prorroga_de = %s and p.prorroga_prorroga_de_id = %s
    """, ('lic',lid))
    for c in cur.fetchall():
        p = {
            'id': c[0],
            'desde': c[1],
            'hasta': c[2],
            'fecha_baja': c[3],
            'tipo_baja': c[4],
            'res': c[5],
            'exp': c[6],
            'cor': c[7],
            'res_baja': c[8],
            'exp_baja': c[9],
            'cor_baja': c[10]
        }
        prorrogas.append(p)
        cargar_prorrogas(cur, p['id'], 'pro', prorrogas)


"""
    ////////////////////////////////////////////////////////
    FUCION PRINCIPAL DE CARGA DE DATOS DEL SILEG VIEJO
    ////////////////////////////////////////////////////////
""" 


def _leer_dnis_de_sileg_viejo(dsn):
    dnis = []
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
    return dnis

def cargar_datos(dsn, dni):
    """
        obtiene la información de todas las designaciones,prorrogas,extensiones y licencias de la persona
        desde el sileg antiguo
    """
    functions = []

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
                cargar_prorrogas(cur, did, 'des', f['prorrogas'])

                # cargo la info de las extensiones de cada cargo.
                f['extensiones'] = []
                cargar_extensiones(cur, did, f['extensiones'], f['caracter_original'], f['cargo_original'])
                cargar_lugares_y_catedras(cur, f['extensiones'])
                for e in f['extensiones']:
                    #cargo la info de las prorrogas de extensión
                    eid = e['eid']
                    cargar_prorrogas(cur, eid, 'ext', e['prorrogas'])

                # cargo ls licencias de las designaciones originales
                f['licencias'] = []
                cargar_licencias_cargo(cur, did, f['licencias'])

        finally:
            cur.close()
    finally:
        con.close()

    return functions

"""
    /////////////////////////////////////////////////////////////////////////////////

    FUNCIONES AUXILIARES A LAS PRINCIPALES SOBRE SILEG NUEVO!!!

    /////////////////////////////////////////////////////////////////////////////////
"""

def _get_historic(d):
    #return (d['res_baja'] is not None and d['res_baja'] != '') or (d['exp_baja'] is not None and d['exp_baja'] != '') or (d['cor_baja'] is not None and d['cor_baja'] != '')
    return not (d['fecha_baja'] is None or d['fecha_baja'] > datetime.date.today())

def _obtener_funcion_cargo(session, name):
    """
        Obtiene un objeto Function a partir de un nombre de cargo/función
    """
    fs = silegModel.get_functions_by_name(session, name)
    if not fs or len(fs) <= 0:
        #archivo.write(f"{dni};No se encuentra la función;{p['funcion']}\n")
        #raise Exception(f"No se encuentra la fucion {p['funcion']}")
        """ en el caso de que no exista el cargo, lo creo generado en el nuevo sileg """
        fid = str(uuid.uuid4())
        function = Function()
        function.id = fid
        function.type = FunctionTypes.DOCENTE
        function.name = name
        function.description = 'IMPORTADO SILEG'
        session.add(function)
        session.commit()
        fs = silegModel.get_functions_by_name(session, name)
    func = fs[0]
    return func

def _obtener_catedra(session, name):
    """
        obtiene el id de una catedra por nombre, en el caso de que no exista la crea
    """
    cs = silegModel.get_places_by_name(session, name)
    if not cs or len(cs) <= 0:
        pid = str(uuid.uuid4())
        lugar = Place()
        lugar.id = pid
        lugar.name = name
        lugar.type = PlaceTypes.CATEDRA
        session.add(lugar)
        session.commit()
        cs = silegModel.get_places_by_name(session, name)
    c = cs[0]
    return c

def _obtener_lugar(session, name):
    """
        obtiene el id de un lugar por nombre, en el caso de que no exista lo crea
    """
    cs = silegModel.get_places_by_name(session, name)
    if not cs or len(cs) <= 0:
        pid = str(uuid.uuid4())
        lugar = Place()
        lugar.id = pid
        lugar.name = name
        lugar.type = PlaceTypes.AREA
        session.add(lugar)
        session.commit()
        cs = silegModel.get_places_by_name(session, name)
    c = cs[0]
    return c

"""
@event.listens_for(Session, 'after_transaction_create')
def _pts(s, t):
    print('transacción iniciada')

@event.listens_for(Session, 'after_transaction_end')
def _pte(s, t):
    print('transacción finalizada')
"""

def _generar_baja(session, uid, designacion_id, function_id, place_id, desig):
    """
        Genera una baja de la designación asociada por designation_id
    """
    db = Designation()
    db.type = DesignationTypes.DISCHARGE
    db.end_type = DesignationEndTypes.INDETERMINATE
    db.designation_id = designacion_id
    db.user_id = uid
    db.function_id = function_id
    db.place_id = place_id
    db.start = desig['fecha_baja']
    db.res = desig['res_baja']
    db.exp = desig['exp_baja']
    db.cor = desig['cor_baja']
    db.historic = True
    db.comments = desig['baja_comments']
    session.add(db)
    session.commit()


def _generar_prorrogas(session, uid, designacion_id, function_id, place_id, desig):
    """
        Genera las prorrogas necesarias dentro del nuevo modelo
        desig = datos cargados del modelo viejo del sileg
        function_id = id de cargo a configurar
        place_id = id de lugar a configurar
        designation_id = id de la designación original
    """
    for p in desig['prorrogas']:
        historic = _get_historic(p)

        prorroga_id = str(uuid.uuid4())
        dp = Designation()
        dp.id = prorroga_id
        dp.type = DesignationTypes.EXTENSION
        dp.end_type = DesignationEndTypes.INDETERMINATE        
        dp.user_id = uid
        dp.function_id = function_id
        dp.place_id = place_id
        dp.designation_id = designacion_id
        dp.res = p['res']
        dp.exp = p['exp']
        dp.cor = p['cor']
        dp.start = p['desde']
        dp.end = p['hasta']
        dp.historic = historic
        session.add(dp)
        session.commit()

        if historic:
            _generar_baja(session, uid, prorroga_id, function_id, place_id, p)


def _generar_extension_cargo_original(session, uid, designacion_id, function_id, place_id, extension):
        """
            Genera una extensión con sus prorrogas y bajas.
            extension = datos cargados del sileg viejo
            place_id = lugar de trabajo
            function_id = cargo a desempeñar
            designacion_id = designación original la cual se extiende
            uid = id del usuario
        """
        extension_id = str(uuid.uuid4())
        historic = _get_historic(extension)

        dp = Designation()
        dp.id = extension_id
        dp.type = DesignationTypes.PROMOTION
        dp.end_type = DesignationEndTypes.INDETERMINATE
        dp.user_id = uid
        dp.designation_id = designacion_id
        dp.function_id = function_id
        dp.place_id = place_id
        dp.res = extension['res']
        dp.cor = extension['cor']
        dp.exp = extension['exp']
        dp.start = extension['desde']
        dp.end = extension['hasta']
        dp.historic = historic
        session.add(dp)
        session.commit()

        if historic:
            _generar_baja(session, uid, extension_id, function_id, place_id, extension)
    
        if 'prorrogas' in extension and len(extension['prorrogas']) > 0:
            _generar_prorrogas(session, uid, extension_id, function_id, place_id, extension)

        return extension_id


def _generar_cargo_original(session, uid, function_id, place_id, desig):
    """
        Genera una designación original.
        session = sesión de sqlalchemy al sileg nuevo
        uid = id del usuario
        function_id = id del cargo a cumplir
        place_id = id del lugar de trabajo de la designación.
        desig = datos cargados de la designación del sileg anterior
    """    
    designacion_id = str(uuid.uuid4())
    historic = _get_historic(desig)

    d = Designation()
    d.id = designacion_id
    d.type = DesignationTypes.ORIGINAL
    d.designation_id = None
    d.res = desig['res']
    d.exp = desig['exp']
    d.cor = desig['cor']
    d.start = desig['desde']
    d.end = desig['hasta']
    d.comments = desig['comentarios']
    d.end_type = DesignationEndTypes.INDETERMINATE

    d.user_id = uid
    d.function_id = function_id
    d.place_id = place_id
    d.historic = historic
    session.add(d)
    session.commit()

    """
        ver la convalidación
    """
    if desig['convalidada']:
        dc = DesignationConvalidation()
        dc.id = str(uuid.uuid4())
        dc.designation_id = designacion_id
        dc.convalidation = desig['convalidada']
        session.add(dc)
        session.commit()
        
    """
        ajustada a la ordenanza
    """
    if desig['ord']:
        da = DesignationAdjusted()
        da.id = str(uuid.uuid4())
        da.designation_id = designacion_id
        da.exp = desig['ord_exp']
        da.res = desig['ord_res']
        da.cor = desig['ord_cor']
        da.start = desig['ord_desde']
        da.end = desig['ord_hasta']
        session.add(da)
        session.commit()

    """
        para el procesamiento de los reemplazos.
        se generan 2 etiquetas:
        sileg_viejo_id = id de la desig en sileg viejo
        sileg_viejo_replacement = id de la designacion relacionada en sileg viejo que seria la que esta cubriendo el reemplazo
    """
    dl = DesignationLabel()
    dl.designation_id = designacion_id
    dl.id = str(uuid.uuid4())
    dl.name = 'sileg_viejo_id'
    dl.value = desig['did']
    session.add(dl)

    if desig['reemplazo_de_id']:
        dl = DesignationLabel()
        dl.designation_id = designacion_id
        dl.id = str(uuid.uuid4())
        dl.name = 'sileg_viejo_replacement'
        dl.value = desig['reemplazo_de_id']
        session.add(dl)
    session.commit()

    if historic:
        _generar_baja(session, uid, designacion_id, function_id, place_id, desig)
 
    if 'prorrogas' in desig and len(desig['prorrogas']) > 0:
        _generar_prorrogas(session, uid, designacion_id, function_id, place_id, desig)

    return designacion_id

"""
    /////// LICENCIAS /////////////
"""

def _descripcion_licencia_a_tipo(desc):
    if 'Renta Suspendida' in desc:
        return LicenseTypes.SUSPENDED_PAYMENT
    if 'Retención de Cargo' in desc:
        return LicenseTypes.DESIGNATION_RETENTION
    if 'Suspension Transitoria' in desc:
        return LicenseTypes.TRANSITORY_SUSPENSION
    if 'Licencia' in desc:
        return LicenseTypes.LICENSE
    if 'Art. 46' in desc:
        return LicenseTypes.ART46

def _generar_baja_licencia(session, licence_id, licence):
    """
        Genera una baja de una licencia
    """
    db = DesignationLeaveLicense()
    db.type = LicenseTypes.DISCHARGE
    db.end_type = LicenseEndTypes.LICENSE_END
    db.designation_id = None
    db.license_id = licence_id
    
    db.start = licence['fecha_baja']
    db.res = licence['res_baja']
    db.exp = licence['exp_baja']
    db.cor = licence['cor_baja']
    db.historic = True
    session.add(db)
    session.commit()

def _generar_prorrogas_licencia(session, licencia_id, licencia):
    """
        Genera las prorrogas necesarias dentro del nuevo modelo
    """
    for p in licencia['prorrogas']:
        historic = _get_historic(p)

        prorroga_id = str(uuid.uuid4())
        dp = DesignationLeaveLicense()
        dp.id = prorroga_id
        dp.license_id = licencia_id
        dp.designation_id = None
        dp.type = LicenseTypes.EXTENSION
        dp.end_type = LicenseEndTypes.INDETERMINATE

        dp.res = p['res']
        dp.exp = p['exp']
        dp.cor = p['cor']
        dp.start = p['desde']
        dp.end = p['hasta']
        dp.historic = historic
        session.add(dp)
        session.commit()

        if historic:
            _generar_baja_licencia(session, prorroga_id, p)


def _generar_licencia_cargo_original(session, designacion_id, licencia):
        """
            Genero una licencia de la designacion
        """
        lid = str(uuid.uuid4())
        historic = _get_historic(licencia)

        dp = DesignationLeaveLicense()
        dp.id = lid
        dp.type = _descripcion_licencia_a_tipo(licencia['tipo_lic'])
        dp.end_type = LicenseEndTypes.INDETERMINATE
        
        dp.designation_id = designacion_id
        dp.res = licencia['res']
        dp.cor = licencia['cor']
        dp.exp = licencia['exp']
        dp.start = licencia['desde']
        dp.end = licencia['hasta']
        dp.historic = historic
        session.add(dp)
        session.commit()

        if historic:
            _generar_baja_licencia(session, lid, licencia)
    
        if 'prorrogas' in licencia and len(licencia['prorrogas']) > 0:
            _generar_prorrogas_licencia(session, lid, licencia)

        return lid



"""
    /////////////////////////////////////////////////////////////////////////////////
    FUNCTION PRINCIPAL PARA GENERAR LOS CARGOS DE UNA PERSONA DENTRO DEL MODELO NUEVO
    /////////////////////////////////////////////////////////////////////////////////
"""
def generar_cargos(silegSession, functions, uid, dni):
    """
        genera todos los cargos, extensiones, prorrogas y licencias de una persona.
    """

    for function in functions:
        cargo = _obtener_funcion_cargo(silegSession, function['funcion'])
        if 'lugar' in function and function['lugar']:
            lugar = _obtener_lugar(silegSession, function['lugar'])
        elif 'catedra' in function and function['catedra']:
            lugar = _obtener_catedra(silegSession, function['catedra'])            
        if not lugar:
            raise Exception(f'No se encuentra lugar de trabajo para {uid} {dni}')
        
        """ genero la designacion con todas sus prorrogas y bajas """
        did = _generar_cargo_original(silegSession, uid, cargo, lugar, function)

        """ 
            genero las extensiones de la designacion original, con sus prorrogas y bajas 
        """
        if 'extensiones' in function and len(function['extensiones']) > 0:
            for extension in function['extensiones']:
                ecargo = _obtener_funcion_cargo(silegSession, extension['funcion'])
                ecatedra = None
                if 'catedra' in extension and extension['catedra']:
                    ecatedra = _obtener_catedra(silegSession, extension['catedra'])
                elugar = None
                if 'lugar' in extension and extension['lugar']:
                    elugar = _obtener_lugar(silegSession, extension['lugar'])
                if not lugar:
                    raise Exception(f'No se encuentra lugar de trabajo de la extension para {uid} {dni}')

                """
                    TEMA IMPORTANTE A ANALIZAR.
                    SILEG VIEJO PERMITE ASOCIAR UNA DESIGNACION A 2 LUGARES A LA VEZ. (MATERIA, AREA)
                    EN EL NUEVO NO SE PERMITE (ES REDUNDANTE E INCORRECTO)
                    ASI QUE SE GENERA LA EXTENSIÓN DENTRO DEL LUGAR QUE DIFIERE DEL CARGO ORIGINAL
                """
                elugar_asociado = None
                if ecatedra and not elugar:
                    elugar_asociado = ecatedra
                if elugar and not ecatedra:
                    elugar_asociado = elugar
                if ecatedra and elugar:
                    if ecatedra == lugar:
                        elugar_asociado = elugar
                    elif elugar == lugar:
                        elugar_asociado = ecatedra
                    else:
                        """ en el caso de que no se pueda determinar se le da prioridad al lugar """
                        elugar_asociado = elugar

                """ ahora si con los datos genero el arbol de extension """
                _generar_extension_cargo_original(silegSession, uid, did, ecargo, elugar_asociado, extension)


        """
            genero las licencias del cargo original
        """
        if 'licencias' in function and len(function['licencias']) > 0:
            for license in function['licencias']:
                print(f"generando licencia {did} - {license['tipo_lic']}")
                _generar_licencia_cargo_original(silegSession, did, license)



"""
    /////////////////////////////////////////////////7
    FUNCIONES AUXILIARES A LA OPERATORIA DEL SCRIPT
    ///////////////////////////////////////////////////
"""

def _eliminar_designaciones_anteriores(session, uid):
    try:
        """ 
            elimino fisicamente todas las designaciones de la persona referenciada 
            las designaciones tienen hasta 2 niveles de indirección.
            y las licencias también.
            o sea que a  lo sumo puede haber hasta 3 niveles en total de anidamiento parmiento de una designación.

            designacion --> 
                  baja
                  prorroga --> 
                      baja

                  licencia -->
                     baja
                     prorroga -->
                        baja 

            persona -->
                licencia -->
                   baja
                   prorroga -->
                      baja

        """
        pls = session.query(PersonalLeaveLicense).filter(PersonalLeaveLicense.user_id == uid).all()
        for l in pls:
            ''' licencias '''
            for lp in l.licences:
                ''' prorrogas '''
                for lb in lp.licences:
                    ''' bajas '''
                    session.delete(lb)
                    session.commit()
                session.delete(lp)
                session.commit()
            session.delete(l)
            session.commit()

        desigs = session.query(Designation).filter(Designation.user_id == uid).all()
        for d in desigs:
            ''' elimino las licencias que tenga '''
            ls = session.query(DesignationLeaveLicense).filter(DesignationLeaveLicense.designation_id == d.id).all()
            for l in ls:
                ''' prorrogas '''
                for lp in l.licences:
                    ''' bajas '''
                    for baja in lp.licences:
                        session.delete(baja)
                        session.commit()
                    session.delete(lp)
                    session.commit()
                session.delete(l)
                session.commit()

            """
                la eliminación física de las designaciones es muy costosa.
                asi que las actualzio para dejarlas sin usuario, ni designacion asociada.
                asi son procesadas por otro script en background para ser elimnadas
            """
            for dp in d.designations:
                for baja in dp.designations:
                    baja.designation_id = None
                    baja.user_id = None
                    baja.place_id = None
                    baja.comments = 'TODELETE'
                    session.commit()
                dp.designation_id = None
                dp.user_id = None
                dp.place_id = None
                dp.comments = 'TODELETE'
                session.commit()
            print(f'marcando para eliminar {d.id}')
            d.user_id = None
            d.designation_id = None
            d.place_id = None
            d.comments = 'TODELETE'
            session.commit()
            
            """
            for dp in d.designations:
                ''' prorrogas '''
                for baja in dp.designations:
                    ''' bajas '''
                    session.delete(baja)
                    session.commit()
                session.delete(dp)
                session.commit()

            print(f'eliminando la designacion original {d.id}')
            session.delete(d)
            session.commit()
            """

    except Exception as e:
        print(e)
        logging.exception(e)


def _buscar_o_crear_usuario_uid(dni):
    with open_users_session() as session:
        uid = UsersModel.get_uid_person_number(session, dni)
        if not uid:
            uid = str(uuid.uuid4())
            user = User()
            user.id = uid
            user.name = 'Importado del sileg.'
            user.lastname = 'Importado del sileg'
            session.add(user)

            idni = IdentityNumber()
            idni.id = str(uuid.uuid4())
            idni.number = dni
            idni.user_id = uid
            session.add(idni)

            session.commit()
            
    return uid

def _leer_dnis_ya_procesados():
    """
        leo los dnis que ya fueron migrados.
    """
    dnis_ya_migrados = []
    with open('migracion-cargos-sileg.csv','r') as archivo:
        for l in archivo:
            dni = l.split(';')[0]
            if dni not in dnis_ya_migrados:
                print(f"agregando dni {dni} a la lista de migrados")
                dnis_ya_migrados.append(dni)
    return dnis_ya_migrados

def _dump_de_funciones_json(functions):
    if functions and len(functions) > 0:
        with open('cargos-leidos.csv', 'a') as acargos:
            dni = functions[0]['dni']
            acargos.write('{')
            acargos.write(f'"{dni}":')
            acargos.write(json.dumps(functions, default=json_serial))
            acargos.write('}')


if __name__ == '__main__':

    dsn = sys.argv[2]
    dni_seleccionado = sys.argv[1]

    if dni_seleccionado == '1':
        #dnis_ya_migrados = _leer_dnis_ya_procesados()
        dnis_ya_migrados = []
        dnis = _leer_dnis_de_sileg_viejo(dsn)
        dnis_a_procesar = [d for d in dnis if d not in dnis_ya_migrados]
    else:
        dnis_a_procesar = [dni_seleccionado]

    cantidad_total = len(dnis_a_procesar)
    cantidad_actual = 0

    for dni in dnis_a_procesar:
        """ imprimo una cabecera para iniciar el proceso """
        cantidad_actual = cantidad_actual + 1
        print(f"DNI: {dni} -- {cantidad_actual}/{cantidad_total}")
        
        """ cargo los datos del sileg antiguo """
        functions = cargar_datos(dsn, dni)

        print('escribiendo archivo intermedio de cargos')
        _dump_de_funciones_json(functions)

        print(f'buscando usuario {dni}')
        uid = _buscar_o_crear_usuario_uid(dni)

        
        silegModel = SilegModel()
        with open_session(echo=False) as session:
            try:
                print(f'eliminando designaciones anteriores de {dni} - {uid}')
                _eliminar_designaciones_anteriores(session, uid)
                
                print(f'generando información de cargos dentro de la base nueva para {dni} - {uid}')
                generar_cargos(session, functions, uid, dni)

            except Exception as e:
                print(e)
                logging.exception(e)
