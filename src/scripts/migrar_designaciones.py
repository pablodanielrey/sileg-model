import sys
import psycopg2

functions = []

dsn = sys.argv[1]
con = psycopg2.connect(dsn=dsn)
try:
    cur = con.cursor()
    try:
        cur.execute("select tipodedicacion_nombre, tipocaracter_nombre, tipocargo_nombre from designacion_docente dd left join tipo_dedicacion td on (dd.desig_tipodedicacion_id = td.tipodedicacion_id) left join tipo_caracter tc on (dd.desig_tipocaracter_id = tc.tipocaracter_id) left join tipo_cargo tcc on (dd.desig_tipocargo_id = tcc.tipocargo_id)")
        for p in cur:
            functions.append({
                'd':p[0],
                'c':p[1],
                'cc':p[2]
            })
            
    finally:
        cur.close()
finally:
    con.close()

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


from sileg_model.model.entities.Function import Function, FunctionTypes
from sileg_model.model import open_session
from sileg_model.model.SilegModel import SilegModel

silegModel = SilegModel()
with open_session() as session:
    try:
        for p in functions:
            nname = transform_name_to_new_model(p['d'], p['c'], p['cc'])
            fs = silegModel.get_functions_by_name(session, nname)
            if not fs or len(fs) <= 0:
                print(f'la función no existe : {nname}')

    except Exception as e:
        print(e)