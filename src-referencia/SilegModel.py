from sqlalchemy import or_,and_, func
from sqlalchemy.orm import joinedload, with_polymorphic, selectin_polymorphic
import datetime
import requests
import os
import logging
import uuid
import json
import re

from .entities import *


"""
    ###############
    para la cache de usuarios

from model_utils.API import API
from model_utils.UserCache import MongoUserCache
from model_utils.UsersAPI import UsersAPI

    ###############

VERIFY_SSL = bool(int(os.environ.get('VERIFY_SSL',0)))
USERS_API = os.environ['USERS_API_URL']
OIDC_URL = os.environ['OIDC_URL']
OIDC_CLIENT_ID = os.environ['OIDC_CLIENT_ID']
OIDC_CLIENT_SECRET = os.environ['OIDC_CLIENT_SECRET']
REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
MONGO_URL = os.environ['MONGO_URL']

_API = API(url=OIDC_URL, 
              client_id=OIDC_CLIENT_ID, 
              client_secret=OIDC_CLIENT_SECRET, 
              verify_ssl=VERIFY_SSL)

_USERS_API = UsersAPI(api_url=USERS_API, api=_API)

class UA:

    def __init__(self, api_url, api):
        self.url = api_url
        self.api = api
"""

class SilegModel:

    @classmethod
    def _config(cls):
        volumen = os.environ['VOLUMEN_CONFIG']
        with open(volumen + '/config.json','r') as f:
            config = json.load(f)
        return config

    @staticmethod
    def _chequearParam(param, d):
        assert param in d
        assert d[param] is not None

    """
        //////// método necesario para el script de chequear cuentas en google ////////
    """

    @classmethod
    def obtener_uids(cls, session):
        """
            retorna todos los usuarios que tengan designacion sin repetir
        """
        ds = session.query(Designacion.usuario_id).distinct()
        return [d.usuario_id for d in ds]

    """
        ///////////////////////// métodos sileg-ui /////////////////////
    """


    @classmethod
    def usuarios_admin_search(cls, session, autorizador_id, search):
        """
        uids = cls.cache_usuarios.obtener_uids()
        usuarios = cls.cache_usuarios.obtener_usuarios_por_uids(uids)

        ''' mejoro un poco el texto de search para que matchee la cadena de nombre apellido dni'''
        rsearch = '.*{}.*'.format(search.replace('.','').replace(' ', '.*'))
        r = re.compile(rsearch, re.I)
        filtrados = [ u for u in usuarios if r.match(u['nombre'] + ' ' + u['apellido'] + ' ' + u['dni'])]
        return filtrados        
        """
        usr = _USERS_API._search_user(search)
        return usr

    @classmethod
    def usuarios_search(cls, session, autorizador_id, search):
        """
            hay que manejar perfiles de acceso a los datos de usuarios.
            por ejemplo ciertas oficinas se encargan de ciertos tipos de usuario definidos por los cargos
            DeTISE --> docentes
            DiTESI --> ADMIN
            Personal --> ADMIN
            Departamentos --> usuarios dentro del departamento

            por ahora solo retorno todos los que tengan designacion
        """
        ds = session.query(Designacion.usuario_id).distinct()
        uids = [u[0] for u in ds]
        usuarios = cls.cache_usuarios.obtener_usuarios_por_uids(uids)

        ''' mejoro un poco el texto de search para que matchee la cadena de nombre apellido dni'''
        rsearch = '.*{}.*'.format(search.replace('.','').replace(' ', '.*'))
        r = re.compile(rsearch, re.I)
        filtrados = [ u for u in usuarios if r.match(u['nombre'] + ' ' + u['apellido'] + ' ' + u['dni'])]
        return filtrados

    """
        /////////////////////////////////////////////////////////////////
    """


    @classmethod
    def crearDesignacionCumpliendoFunciones(cls, session, pedido):
        cls._chequearParam('usuario_id', pedido)
        cls._chequearParam('lugar_id', pedido)

        uid = pedido['usuario_id']

        ''' genero la designacion con los datos pasados '''
        cf = Cargo(id='245eae51-28c4-4c6b-9085-354606399666', nombre='Cumple Funciones', tipo=Cargo._tipos[1])

        d = Designacion()
        d.id = str(uuid.uuid4())
        d.tipo = 'original'
        d.desde = datetime.datetime.now()
        d.usuario_id = uid
        d.cargo_id = cf.id
        d.lugar_id = pedido['lugar_id']
        session.add(d)
        return d

    @classmethod
    def crearDesignacion(cls, session, usuario_id, cargo_id, lugar_id, desde):
        d = Designacion()
        d.id = str(uuid.uuid4())
        d.desde = desde if desde else datetime.datetime.now()
        d.usuario_id = usuario_id
        d.cargo_id = cargo_id
        d.lugar_id = lugar_id
        session.add(d)
        return d.id
  
    @classmethod
    def _agregar_filtros_comunes(cls, q, persona=None, lugar=None, offset=None, limit=None):
        q = q.filter(Designacion.usuario_id == persona) if persona else q
        q = q.filter(Designacion.lugar_id == lugar) if lugar else q
        q = q.offset(offset) if offset else q
        q = q.limit(limit) if limit else q
        return q

    @classmethod
    def chequear_acceso_designaciones(cls, session, usuario_logueado, uid):
        assert usuario_logueado is not None
        assert uid is not None

        ''' ahora chequeamos que el usuario logueado tenga permisos para consultar las designaciones de uid '''

        return usuario_logueado == uid


    @classmethod
    def cargos(cls, session):
        """
        cargos = with_polymorphic(Cargo,[
            Docente,
            CumpleFunciones,
            NoDocente
        ])
        return session.query(cargos).all()
        """
        return session.query(Cargo).all()


    @classmethod
    def obtener_catedras_por_nombre(cls, session, search=None):
        q = None
        if not search:
            q = session.query(Catedra)
        else:
            q2 = session.query(Materia.id).filter(Materia.nombre.op('~*')(search))
            q = session.query(Catedra).filter(or_(Catedra.materia_id.in_(q2), Catedra.nombre.op('~*')(search)))
        return q.options(joinedload('materia')).all()


    @classmethod
    def lugares(cls, session, search=None):
        lugares = with_polymorphic(Lugar,[
            Direccion,
            Escuela,
            LugarDictado,
            Secretaria,
            Instituto,
            Prosecretaria,
            Maestria,
            Catedra
        ])

        q = None
        if not search:
            q = session.query(lugares)
        else:
            ''' TODO: no se como sacar la subclase Catedra de la consulta. analizar otras posibilidades. ahora esta filtrado '''
            q = session.query(lugares).filter(lugares.Catedra.id == None, lugares.nombre.op('~*')(search))
        return q.all()

    @classmethod
    def lugar(cls, session, lid):

        query = session.query(Lugar).options(
            selectin_polymorphic(Lugar, [Direccion,Escuela,LugarDictado,Secretaria,Instituto,Prosecretaria,Maestria,Catedra]),
            joinedload(Catedra.materia)
        )
        return query.filter(Lugar.id == lid).one_or_none()


    @classmethod
    def departamentos(cls, session):
        return Departamento.find(session).all()

    @classmethod
    def materias(cls, session, materia=None, catedra=None, departamento=None):
        q = Materia.find(session)
        q = q.filter(Materia.id == materia) if materia else q
        q = q.join(Catedra).filter(Catedra.id == catedra) if catedra else q
        q = q.join(Catedra).filter(Catedra.padre_id == departamento) if departamento else q
        return q.all()

    @classmethod
    def catedras(cls, session, catedra=None, materia=None, departamento=None):
        q = Catedra.find(session)
        q = q.filter(Catedra.id == catedra) if catedra else q
        q = q.filter(Catedra.materia_id == materia) if materia else q
        q = q.filter(Catedra.padre_id == departamento) if departamento else q
        return q.options(joinedload('materia'), joinedload('padre')).all()

    @classmethod
    def crearLugar(cls, session, lugar):
        cls._chequearParam('nombre', lugar)
        cls._chequearParam('tipo', lugar)

        # verifico que no exista el lugar
        lugares = with_polymorphic(Lugar,[
            Direccion,
            Escuela,
            LugarDictado,
            Secretaria,
            Instituto,
            Prosecretaria,
            Maestria,
            Catedra
        ])
        nombre = lugar["nombre"].strip()
        l = Lugar(nombre)
        l.id = str(uuid.uuid4())
        l.tipo = lugar["tipo"]

        if "descripcion" in lugar and lugar["descripcion"] is not None:
            l.descripcion = lugar["descripcion"]
        else:
            l.descripcion = ''
        if "numero" in lugar and lugar["numero"] is not None:
            l.numero = lugar["numero"]
        else:
            l.numero = ''
        if "telefono" in lugar and lugar["telefono"] is not None:
            l.telefono = lugar["telefono"]
        else:
            l.telefono = ''
        if "email" in lugar and lugar["email"] is not None:
            l.correo = lugar["email"]
        else:
            l.correo = ''
        session.add(l)
        return l

    @classmethod
    def modificarLugar(cls, session, lugar):
        cls._chequearParam('nombre', lugar)
        cls._chequearParam('tipo', lugar)
        cls._chequearParam('id', lugar)

        # verifico que no exista el lugar
        lugares = with_polymorphic(Lugar,[
            Direccion,
            Escuela,
            LugarDictado,
            Secretaria,
            Instituto,
            Prosecretaria,
            Maestria,
            Catedra
        ])

        l = session.query(lugares).filter(lugares.id == lugar["id"]).one_or_none()
        if l is None:
            raise Exception("Error, no existe el lugar")

        l.nombre = lugar["nombre"].strip()
        l.descripcion = lugar["descripcion"]
        l.tipo = lugar["tipo"]
        l.numero = lugar["numero"]
        l.telefono = lugar["telefono"]
        l.correo = lugar["correo"]

    @classmethod
    def eliminarLugar(cls, session, lid):
        lugares = with_polymorphic(Lugar,[
            Direccion,
            Escuela,
            LugarDictado,
            Secretaria,
            Instituto,
            Prosecretaria,
            Maestria,
            Catedra
        ])

        l = session.query(lugares).filter(lugares.id == lid).one()
        l.eliminado = datetime.datetime.now()
        return l.eliminado

    @classmethod
    def restaurarLugar(cls, session, lid):
        lugares = with_polymorphic(Lugar,[
            Direccion,
            Escuela,
            LugarDictado,
            Secretaria,
            Instituto,
            Prosecretaria,
            Maestria,
            Catedra
        ])

        l = session.query(lugares).filter(lugares.id == lid).one()
        l.eliminado = None
        return l.id


    @staticmethod
    def _ordernar_designaciones_por_fecha(d):
        if d.desde:
            return d.desde
        return datetime.date(1900,1,1)


    @classmethod
    def designaciones(cls,
                    session,
                    offset=None, limit=None,
                    persona=None,
                    lugar=None,
                    historico=False, expand=False):

        #q = Designacion.find(session)
        q = Designacion.find(session).filter(or_(Designacion.tipo == None, Designacion.tipo == 'original'))
        if not historico:
            q = q.filter(or_(Designacion.historico == None, Designacion.historico == False))

        q = q.order_by(Designacion.desde.desc())
        q = cls._agregar_filtros_comunes(q, offset=offset, limit=limit, persona=persona, lugar=lugar)
        if expand:
            if not lugar:
                q = q.options(joinedload('lugar').joinedload('padre'))
            q = q.options(joinedload('cargo'))
        r = q.all()
        return sorted(r, key=SilegModel._ordernar_designaciones_por_fecha)

    @classmethod
    def obtener_designaciones_docentes_por_persona(cls, session, persona):
        pass

    @classmethod
    def obtener_designaciones_no_docentes_por_persona(cls, session, persona):
        pass

    @classmethod
    def detalleDesignacion(cls, session, did):
        designaciones = {}
        d = session.query(Designacion).filter(Designacion.id == did).one()

        ''' me muevo a la raiz del arbol de designaciones '''
        while d.designacion_id is not None:
            d = session.query(Designacion).filter(Designacion.id == d.designacion_id).one()
        
        a_procesar = set()
        a_procesar.add(d)

        ''' proceso los hijos '''
        while len(a_procesar) > 0:
            r = a_procesar.pop()
            if r.id not in designaciones:
                designaciones[r.id] = r
                relacionadas = session.query(Designacion).filter(Designacion.designacion_id == r.id).all()
                a_procesar.update(relacionadas)


        retorno = []
        tk = cls.api._get_token()
        for k,d in designaciones.items():
            usr = cls.cache_usuarios.obtener_usuario_por_uid(d.usuario_id, token=tk)
            r = {
                'lugar': d.lugar,
                'usuario': usr,
                'cargo': d.cargo,
                'designacion': d
            }
            retorno.append(r)

        return sorted(retorno, key=lambda d: d['designacion'].desde)

    @classmethod
    def obtenerDesignacionesLugar(cls, session, lid):
        lugar = cls.lugar(session, lid)
        lugares = [lid]
        lugares.extend([l.id for l in lugar.hijos])
                
        # obtengo las designaciones del lugar
        tk = cls.api._get_token()
        designaciones = []
        for llid in lugares:
            desig = cls.designaciones(session=session, lugar=llid, historico=True)
            for d in desig:
                usr = cls.cache_usuarios.obtener_usuario_por_uid(d.usuario_id, token=tk)
                r = {
                    'designacion': d,
                    'usuario': usr,
                    'cargo': d.cargo,
                    'lugar': d.lugar
                }
                designaciones.append(r)

        return { 'lugar':lugar, 'designaciones': designaciones }


    @classmethod
    def eliminarDesignacion(cls, session, id):
        l = session.query(Designacion).filter(Designacion.id == id).one()
        l.historico = True

    @classmethod
    def actualizarDesignacion(cls, session, id, designacion):
        d = session.query(Designacion).filter(Designacion.id == id).one_or_none()
        if d is None:
            raise Exception("Error, no existe la designación")

        d.desde = designacion["desde"]
        d.cargo_id = designacion["cargo_id"]

    @classmethod
    def obtener_usuarios(cls, session):
        """
            retorna todos los usuarios que tengan designacion
        """
        ds = session.query(Designacion)
        registros = [
            {
                'usuario': d.usuario_id,
                'cargo': d.cargo.nombre if d.cargo else '',
                'lugar': d.lugar.nombre if d.lugar else ''
            }
            for d in ds
        ]
        return registros


    @classmethod
    def obtener_subusuarios_por_usuario(cls, session, uid):
        """
            retorna todos los usuarios que están en la misma oficina que el usuario uid, o en suboficinas de esta
        """
        lugares = cls.obtener_lugares_por_usuario(session, uid)
        usuarios = cls.obtener_subusuarios_por_lugares(session, lugares)
        return usuarios

    @classmethod
    def obtener_subusuarios_por_lugares(cls, session, lids=[]):
        """
            retorna todos los usuarios que tienen designaciones en los arboles de lugares que tienen como raiz los
            ids dados en lids
        """
        lugares = []
        for lid in lids:
            lugares.append(lid)
            cls.obtener_sublugares(session, lid, lugares)

        usuarios = []
        for lid in lugares:
            registros = cls.obtener_usuarios_por_lugar(session, lid)
            usuarios.extend(registros)

        return usuarios

    @classmethod
    def obtener_lugares_por_usuario(cls, session, uid):
        ds = session.query(Designacion.lugar_id).filter(Designacion.usuario_id == uid).distinct()
        lugares = [d[0] for d in ds]
        return lugares

    @classmethod
    def obtener_usuarios_por_lugar(cls, session, lid):
        ds = session.query(Designacion).filter(Designacion.lugar_id == lid)
        registros = [
            {
                'usuario': d.usuario_id,
                'cargo': d.cargo.nombre if d.cargo else '',
                'cargo_nivel': d.cargo.nivel if d.cargo else 100,
                'lugar': d.lugar.nombre if d.lugar else ''
            } 
            for d in ds if not d.historico
        ]
        return registros

    @classmethod
    def obtener_sublugares(cls, session, lid, acumulator=[], profundidad_actual=0, profundidad_maxima=5):
        '''
            retorna todos los ids de los lugares que pertenecen al arbol de lugares con raiz == lid
        '''
        if profundidad_actual >= profundidad_maxima:
            """ chequeo de seguridad por el formato del arbol. para no armar loop infinito """
            return

        lids = session.query(Lugar.id).filter(Lugar.padre_id == lid).all()
        acumulator.extend([l[0] for l in lids])
        for lid in lids:
            cls.obtener_sublugares(session, lid, acumulator, profundidad_actual=profundidad_actual + 1)
        return acumulator

    @classmethod
    def obtener_arbol(cls, session, lid, profundidad_actual=0, profundidad_maxima=5):
        '''
            retorna todos los ids de los lugares que pertenecen al arbol de lugares con raiz == lid
        '''
        if profundidad_actual >= profundidad_maxima:
            """ chequeo de seguridad por el formato del arbol. para no armar loop infinito """
            return None

        usuarios = cls.obtener_usuarios_por_lugar(session, lid)

        rlids = session.query(Lugar.id).filter(Lugar.padre_id == lid).all()
        lids = (l[0] for l in rlids)
        hijos = []
        profundidad = profundidad_actual
        for l in lids:
            arbol = cls.obtener_arbol(session, l, profundidad_actual=profundidad_actual + 1)
            hijos.append(arbol)
            profundidad = arbol['profundidad']

        raiz = {
            'lugar': lid,
            'usuarios': usuarios,
            'hijos': hijos,
            'profundidad': profundidad
        }
        return raiz
    