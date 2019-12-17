
from .entities.Function import Function, FunctionTypes

class SilegModel:

    @staticmethod
    def _authority_functions():
        return ['Decano', 'Vicedecano', 'Secretario', 'Prosecretario']

    @staticmethod
    def _teacher_functions():
        functions = ['Adjunto', 'Asociado', 'Ayudante Alumno', 'Ayudante Diplomado', 'Jefe de Auxiliares Docentes', 'Jefe de Trabajos Prácticos']
        dedications = ['Exclusiva', 'Semi Dedicación', 'Semi Exclusiva', 'Simple', 'Tiempo Completo']
        caracters = ['Ad honorem', 'Interino', 'Ordinario', 'Suplente']
        rf = []
        for f in functions:
            for d in dedications:
                for c in caracters:
                    rf.append(f'{f} - {d} - {c}')
        return rf

    def _insert_functions(self, session):
        for f in SilegModel._authority_functions():
            if session.query(Function.id).filter(Function.name == f).count() <= 0:
                ff = Function()
                ff.name = f
                ff.type = FunctionTypes.AUTORIDAD
                session.add(ff)

        for f in SilegModel._teacher_functions():
            if session.query(Function.id).filter(Function.name == f).count() <= 0:
                ff = Function()
                ff.name = f
                ff.type = FunctionTypes.DOCENTE
                session.add(ff)

    def get_functions(self, session):
        return session.query(Function).all()
