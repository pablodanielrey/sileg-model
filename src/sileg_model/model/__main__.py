
def create_tables():
    import os
    from sqlalchemy import create_engine
    from .entities.Function import Function, FunctionTypes
    from .entities.Designation import Designation, DesignationEndTypes, DesignationAdjusted, DesignationConvalidation, DesignationLabel
    from .entities.Place import PlaceTypes, Place
    from .entities.LeaveLicense import PersonalLeaveLicense, DesignationLeaveLicense
    from .entities.ExternalSeniority import ExternalSeniority
    from .entities import Base
    engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(
        os.environ['SILEG_DB_USER'],
        os.environ['SILEG_DB_PASSWORD'],
        os.environ['SILEG_DB_HOST'],
        os.environ['SILEG_DB_PORT'],
        os.environ['SILEG_DB_NAME']
    ), echo=True)
    Base.metadata.create_all(engine)    


def insert_model_data():
    """
        Se generan los datos para inicializar la base de datos.
    """

    from sileg_model.model import open_session
    from sileg_model.model.entities.Function import Function, FunctionTypes
    from sileg_model.model.entities.Place import Place, PlaceTypes

    def _authority_functions():
        functions = ['Decano', 'Vicedecano', 'Secretario', 'Prosecretario']
        dedications = ['Exclusiva', 'Simple', 'Tiempo Completo', 'A-H']
        caracters = ['Interino', 'Ad-Honorem']
        rf = []
        for f in functions:
            for d in dedications:
                for c in caracters:
                    rf.append(f'{f} - {d} - {c}')
        return rf


    def _teacher_functions():
        functions = ['Titular', 'Adjunto', 'Asociado', 'Ayudante Alumno', 'Ayudante Diplomado', 'Jefe de Auxiliares Docentes', 'Jefe de Trabajos Prácticos']
        dedications = ['Exclusiva', 'Semi Dedicación', 'Semi Exclusiva', 'Simple', 'Tiempo Completo', 'A-H']
        caracters = ['Ad-Honorem', 'Interino', 'Ordinario', 'Suplente']
        rf = []
        for f in functions:
            for d in dedications:
                for c in caracters:
                    rf.append(f'{f} - {d} - {c}')

        extra = ['Consulto', 'Emérito', 'Visitante']
        for f in functions:
            for e in extra:
                rf.append(f'{f} - {e}')

        return rf

    def _insert_functions(session):
        for f in _authority_functions():
            if session.query(Function.id).filter(Function.name == f).count() <= 0:
                ff = Function()
                ff.name = f
                ff.type = FunctionTypes.AUTORIDAD
                session.add(ff)

        for f in _teacher_functions():
            if session.query(Function.id).filter(Function.name == f).count() <= 0:
                ff = Function()
                ff.name = f
                ff.type = FunctionTypes.DOCENTE
                session.add(ff)

    def _get_places():
        return []

    def _insert_places(session):
        for p in _get_places():
            if session.query(Place.id).filter(Place.name == p).count() <= 0:
                pp = Place()
                pp.type = PlaceTypes.DIRECCION
                pp.name = p
                session.add(pp)

    with open_session() as ss:
        _insert_functions(ss)
        #_insert_places(ss)
        ss.commit()

create_tables()
insert_model_data()