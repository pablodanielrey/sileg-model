import sys
import os
import psycopg2

from sileg_model.model.entities.Designation import Designation
from sileg_model.model import open_session
from sileg_model.model.SilegModel import SilegModel
from users.model import open_session as open_users_session
from users.model.UsersModel import UsersModel


if __name__ == '__main__':
    dsn = sys.argv[1]

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

    for dni in dnis:

        try:
            print(f'buscando usuario {dni}')
            with open_users_session() as s2:
                uid = UsersModel.get_uid_person_number(s2, dni)
                if not uid:
                    archivo.write(f'{dni}; No se encuentra un usuario con ese dni\n')
                    raise Exception(f'no se encuentra uid para el dni {dni}')

            silegModel = SilegModel()
            with open_session(echo=False) as session:
                try:
                    """ elimino fisicamente todas las designaciones de la persona referenciada """
                    print(f"eliminando designaciones {dni}")
                    session.query(Designation).filter(Designation.user_id == uid).delete()
                    session.commit()
                except Exception as e:
                    print(e)

        except Exception as e2:
            print(e2)