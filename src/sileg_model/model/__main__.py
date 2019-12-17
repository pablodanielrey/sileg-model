
def insert_model_data():
    """
        Se generan los datos para inicializar la base de datos.
    """

    from sileg_model.model import open_session
    from sileg_model.model.entities.Function import Function, FunctionTypes
    from sileg_model.model.entities.Place import Place, PlaceTypes

    def _authority_functions():
        return ['Decano', 'Vicedecano', 'Secretario', 'Prosecretario']

    def _teacher_functions():
        functions = ['Titular', 'Adjunto', 'Asociado', 'Ayudante Alumno', 'Ayudante Diplomado', 'Jefe de Auxiliares Docentes', 'Jefe de Trabajos Prácticos']
        dedications = ['Exclusiva', 'Semi Dedicación', 'Semi Exclusiva', 'Simple', 'Tiempo Completo']
        caracters = ['Ad honorem', 'Interino', 'Ordinario', 'Suplente']
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
        return [
            'Categra1',
            'DiTeSI',
            'Secretaría Académica'
        ]

    def _insert_places(session):
        for p in _get_places():
            if session.query(Place.id).filter(Place.name == p).count() <= 0:
                pp = Place()
                pp.type = PlaceTypes.DIRECCION
                pp.name = p
                session.add(pp)

    with open_session() as ss:
        _insert_functions(ss)
        _insert_places(ss)
        ss.commit()


from sileg_model.model import create_tables
create_tables()
insert_model_data()