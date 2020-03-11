from sqlalchemy import Column, String, Date, Table, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship

from enum import Enum

from . import Base


"""
    el modelo original contiene varias tablas.
    existen prorrogas de licencias las cuales están asociadas a:

        utndocentes=> \d prorroga
                                                        Table "public.prorroga"
                Column           |         Type          | Collation | Nullable |                    Default                    
        ----------------------------+-----------------------+-----------+----------+-----------------------------------------------
        prorroga_id                | integer               |           | not null | nextval('prorroga_prorroga_id_seq'::regclass)
        prorroga_fecha_obtencion   | date                  |           |          | 
        prorroga_fecha_desde       | date                  |           | not null | 
        prorroga_fecha_hasta       | date                  |           |          | 
        prorroga_tipofincargo_id   | integer               |           |          | 
        prorroga_fecha_baja        | date                  |           |          | 
        prorroga_tipobaja_id       | integer               |           |          | 
        prorroga_resolucionalta_id | integer               |           | not null | 
        prorroga_resolucionbaja_id | integer               |           |          | 
        prorroga_prorrogada_con    | integer               |           |          | 
        prorroga_prorroga_de       | character varying(10) |           | not null | 
        prorroga_idemp             | integer               |           | not null | 
        prorroga_prorroga_de_id    | integer               |           |          | 
        usuario_log                | integer               |           |          | 
        Indexes:
            "prorroga_pkey" PRIMARY KEY, btree (prorroga_id)
        Foreign-key constraints:
            "prorroga_prorroga_idemp_fkey" FOREIGN KEY (prorroga_idemp) REFERENCES empleado(empleado_id)
            "prorroga_prorroga_prorrogada_con_fkey" FOREIGN KEY (prorroga_prorrogada_con) REFERENCES prorroga(prorroga_id)
            "prorroga_prorroga_resolucionalta_id_fkey" FOREIGN KEY (prorroga_resolucionalta_id) REFERENCES resolucion(resolucion_id)
            "prorroga_prorroga_resolucionbaja_id_fkey" FOREIGN KEY (prorroga_resolucionbaja_id) REFERENCES resolucion(resolucion_id)
            "prorroga_prorroga_tipobaja_id_fkey" FOREIGN KEY (prorroga_tipobaja_id) REFERENCES tipo_baja(tipobajadesig_id)
            "prorroga_prorroga_tipofincargo_id_fkey" FOREIGN KEY (prorroga_tipofincargo_id) REFERENCES tipo_fin_cargo(tipofincargo_id)
        Referenced by:
            TABLE "designacion_docente" CONSTRAINT "designacion_docente_desig_prorrogada_con_fkey" FOREIGN KEY (desig_prorrogada_con) REFERENCES prorroga(prorroga_id)
            TABLE "extension" CONSTRAINT "extension_extension_prorrogada_con_fkey" FOREIGN KEY (extension_prorrogada_con) REFERENCES prorroga(prorroga_id)
            TABLE "licencia" CONSTRAINT "licencia_licencia_prorrogada_con_fkey" FOREIGN KEY (licencia_prorrogada_con) REFERENCES prorroga(prorroga_id)
            TABLE "prorroga" CONSTRAINT "prorroga_prorroga_prorrogada_con_fkey" FOREIGN KEY (prorroga_prorrogada_con) REFERENCES prorroga(prorroga_id)
        Triggers:
            prorroga_log AFTER DELETE OR UPDATE ON prorroga FOR EACH ROW EXECUTE PROCEDURE process_prorroga_log()

        utndocentes=> 


        utndocentes=> \d licencia
                                                Table "public.licencia"
                Column           |  Type   | Collation | Nullable |                    Default                    
        ----------------------------+---------+-----------+----------+-----------------------------------------------
        licencia_id                | integer |           | not null | nextval('licencia_licencia_id_seq'::regclass)
        licencia_designacion_id    | integer |           | not null | 
        licencia_articulo_id       | integer |           |          | 
        licencia_fecha_desde       | date    |           | not null | 
        licencia_fecha_hasta       | date    |           |          | 
        licencia_tipofincargo_id   | integer |           |          | 
        licencia_resolucionalta_id | integer |           | not null | 
        licencia_resolucionbaja_id | integer |           |          | 
        licencia_prorrogada_con    | integer |           |          | 
        licencia_fecha_baja        | date    |           |          | 
        licencia_tipobaja_id       | integer |           |          | 
        licencia_tipolicencia_id   | integer |           |          | 
        usuario_log                | integer |           |          | 
        Indexes:
            "licencia_pkey" PRIMARY KEY, btree (licencia_id)
        Foreign-key constraints:
            "licencia_licencia_articulo_id_fkey" FOREIGN KEY (licencia_articulo_id) REFERENCES licencia_articulos(licart_id)
            "licencia_licencia_designacion_id_fkey" FOREIGN KEY (licencia_designacion_id) REFERENCES designacion_docente(desig_id)
            "licencia_licencia_prorrogada_con_fkey" FOREIGN KEY (licencia_prorrogada_con) REFERENCES prorroga(prorroga_id)
            "licencia_licencia_resolucionalta_id_fkey" FOREIGN KEY (licencia_resolucionalta_id) REFERENCES resolucion(resolucion_id)
            "licencia_licencia_resolucionbaja_id_fkey" FOREIGN KEY (licencia_resolucionbaja_id) REFERENCES resolucion(resolucion_id)
            "licencia_licencia_tipobaja_id_fkey" FOREIGN KEY (licencia_tipobaja_id) REFERENCES tipo_baja(tipobajadesig_id)
            "licencia_licencia_tipofincargo_id_fkey" FOREIGN KEY (licencia_tipofincargo_id) REFERENCES tipo_fin_cargo(tipofincargo_id)
            "licencia_licencia_tipolicencia_id_fkey" FOREIGN KEY (licencia_tipolicencia_id) REFERENCES tipo_licencia(tipolicencia_id)
        Triggers:
            licencia_log AFTER DELETE OR UPDATE ON licencia FOR EACH ROW EXECUTE PROCEDURE process_licencia_log()

        utndocentes=> 

        utndocentes=> select * from prorroga where prorroga_prorroga_de = 'lic' limit 10;
        prorroga_id | prorroga_fecha_obtencion | prorroga_fecha_desde | prorroga_fecha_hasta | prorroga_tipofincargo_id | prorroga_fecha_baja | prorroga_tipobaja_id | prorroga_resolucionalta_id | prorroga_resolucionbaja_id | prorroga_prorrogada_con | prorroga_prorroga_de | prorroga_idemp | prorroga_prorroga_de_id | usuario_log 
        -------------+--------------------------+----------------------+----------------------+--------------------------+---------------------+----------------------+----------------------------+----------------------------+-------------------------+----------------------+----------------+-------------------------+-------------
                209 |                          | 2010-05-12           | 2011-03-31           |                          | 2010-05-11          |                      |                       4149 |                       4150 |                         | lic                  |            759 |                      29 |          45
                130 |                          | 2010-03-01           | 2011-02-28           |                          | 2011-02-28          |                    6 |                       3876 |                       3877 |                         | lic                  |            755 |                      14 |            
                135 |                          | 2010-03-01           | 2011-02-28           |                          | 2011-01-31          |                    6 |                       3886 |                       3887 |                         | lic                  |            303 |                       9 |            
                171 |                          | 2010-03-01           | 2011-02-28           |                          |                     |                      |                       3991 |                       3992 |                    1023 | lic                  |            729 |                      60 |          52
                203 |                          | 2010-05-12           | 2014-05-12           |                          | 2018-02-01          |                    5 |                       4084 |                       4085 |                         | lic                  |            474 |                      40 |          52
                360 |                          | 2010-09-01           | 2010-09-30           |                          | 2010-09-30          |                   10 |                       4985 |                       4986 |                         | lic                  |            682 |                       4 |          52
                389 |                          | 2009-08-01           | 2010-04-30           |                          | 2010-05-01          |                    9 |                       5057 |                       5058 |                         | lic                  |            427 |                      65 |          52
                380 | 2009-05-01               | 2010-08-01           |                      |                          | 2010-10-18          |                    6 |                       5034 |                       5035 |                         | lic                  |             56 |                       1 |          45
                413 |                          | 2010-03-01           | 2011-02-28           |                          | 2010-11-30          |                    6 |                       5207 |                       5208 |                         | lic                  |            766 |                      11 |          52
                392 |                          | 2010-08-01           | 2011-07-31           |                          |                     |                      |                       5077 |                       5078 |                    1804 | lic                  |            358 |                      99 |          52
        (10 rows)

        utndocentes=>

        utndocentes=> select * from licencia limit 10
        ;
        licencia_id | licencia_designacion_id | licencia_articulo_id | licencia_fecha_desde | licencia_fecha_hasta | licencia_tipofincargo_id | licencia_resolucionalta_id | licencia_resolucionbaja_id | licencia_prorrogada_con | licencia_fecha_baja | licencia_tipobaja_id | licencia_tipolicencia_id | usuario_log 
        -------------+-------------------------+----------------------+----------------------+----------------------+--------------------------+----------------------------+----------------------------+-------------------------+---------------------+----------------------+--------------------------+-------------
                13 |                     702 |                    3 | 2000-03-01           |                      |                          |                       1503 |                       1504 |                         |                     |                      |                        1 |            
                21 |                     834 |                    3 | 2007-09-01           |                      |                          |                       1978 |                       1979 |                         |                     |                      |                        1 |            
                22 |                     839 |                    3 | 2007-09-01           |                      |                          |                       1995 |                       1996 |                         |                     |                      |                        1 |            
                36 |                     979 |                      | 2009-04-01           | 2010-01-31           |                          |                       2510 |                       2511 |                         |                     |                      |                        3 |            
                46 |                     157 |                      | 2009-09-01           |                      |                          |                       2619 |                       2620 |                         |                     |                      |                        2 |            
                48 |                     208 |                    5 | 2009-04-01           | 2010-03-31           |                          |                       2632 |                       2633 |                         |                     |                      |                        1 |            
                52 |                     738 |                    5 | 2008-03-01           | 2009-02-28           |                          |                       2706 |                       2707 |                         |                     |                      |                        1 |            
                61 |                     417 |                    3 | 2008-06-01           |                      |                          |                       2885 |                       2886 |                         |                     |                      |                        1 |            
                62 |                     422 |                    3 | 2006-06-01           |                      |                          |                       2890 |                       2891 |                         |                     |                      |                        1 |            
                 3 |                     450 |                    4 | 2009-02-01           | 2009-12-31           |                          |                       1252 |                       1253 |                         |                     |                      |                        1 |            
        (10 rows)

        utndocentes=> 


    licencia_id | licencia_fecha_desde | licencia_fecha_hasta | licencia_fecha_baja | licart_descripcion | licart_congocesueldo | resolucion_numero | resolucion_expediente | resolucion_corresponde | resolucion_numero | resolucion_expediente | resolucion_corresponde | tipobajadesig_nombre | tipofincargo_nombre | tipolicencia_descripcion | tipolicencia_abrev 
    -------------+----------------------+----------------------+---------------------+--------------------+----------------------+-------------------+-----------------------+------------------------+-------------------+-----------------------+------------------------+----------------------+---------------------+--------------------------+--------------------
            13 | 2000-03-01           |                      |                     | 41                 | 0                    | 108/00            | 900-21457/00          |                        |                   |                       |                        |                      |                     | Licencia                 | LIC
            21 | 2007-09-01           |                      |                     | 41                 | 0                    | 731/07            | 90-4050/07            |                        |                   |                       |                        |                      |                     | Licencia                 | LIC
            22 | 2007-09-01           |                      |                     | 41                 | 0                    | 739/07            | 900/4051/07           |                        |                   |                       |                        |                      |                     | Licencia                 | LIC
            36 | 2009-04-01           | 2010-01-31           |                     |                    |                      | 138/09            | 900-226/09            |                        |                   |                       |                        |                      |                     | Retención de Cargo       | R/C
            46 | 2009-09-01           |                      |                     |                    |                      | 554/09            | 900-1022/09           |                        |                   |                       |                        |                      |                     | Renta Suspendida         | R/S
            48 | 2009-04-01           | 2010-03-31           |                     | 26                 | 0                    | 122/09            | 900-272/09            |                        |                   |                       |                        |                      |                     | Licencia                 | LIC
            52 | 2008-03-01           | 2009-02-28           |                     | 26                 | 0                    | 126/08            | 900-4550/08           |                        |                   |                       |                        |                      |                     | Licencia                 | LIC
            61 | 2008-06-01           |                      |                     | 41                 | 0                    | 286/08            | 900-4830/08           |                        |                   |                       |                        |                      |                     | Licencia                 | LIC
            62 | 2006-06-01           |                      |                     | 41                 | 0                    | 382/06            | 900-2563/06           |                        |                   |                       |                        |                      |                     | Licencia                 | LIC
             3 | 2009-02-01           | 2009-12-31           |                     | 33                 | 0                    | 696/09            | 900-5613/06           | 01/09                  |                   |                       |                        |                      |                     | Licencia                 | LIC
    (10 rows)

    utndocentes=> 

    utndocentes-> ;
    tipolicencia_id | tipolicencia_descripcion | tipolicencia_abrev | usuario_log 
    -----------------+--------------------------+--------------------+-------------
                2 | Renta Suspendida         | R/S                |            
                3 | Retención de Cargo       | R/C                |            
                4 | Suspension Transitoria   | S/T                |            
                1 | Licencia                 | LIC                |         113
                7 | Art. 46 Inc. C           | Art.46             |          47


    utndocentes=> select  * from tipo_baja;
    tipobajadesig_id |  tipobajadesig_nombre   | usuario_log 
    ------------------+-------------------------+-------------
                    1 | Fallecimiento           |            
                    5 | Renuncia                |            
                    9 | Término de Designación  |          45
                   11 | Cambio de Cátedra       |          45
                    7 | Termino de Extensión    |          47
                    6 | Limitación de Funciones |          47
                   10 | Térrmino de Licencia    |          47
                    8 | Cambio de Licencia      |          47
                   12 | reintegro de licencia   |         113
                   13 | Jubilación              |          99
                   14 | Limitacion de Cargo     |         139
    (11 rows)                
"""


class LicenseTypes(Enum):
    INDETERMINATE = 'INDETERMINATE'
    SUSPENSION = 'SUSPENSION'
    TRANSITORY_SUSPENSION = 'TRANSITORY_SYSPENSION'
    SUSPENDED_PAYMENT = 'SUSPENDED_PAYMENT'
    DESIGNATION_RETENTION = 'DESIGNATION_RETENTION'
    LICENCE = 'LICENCE'
    EXTENSION = 'EXTENSION'
    DISCHARGE = 'DISCHARGE'

"""
Esto es lo que se encuentra en la base pero me suena a que es una baja de cargo, no un tipo de fin de licencia!!.


"""
class LicenseEndTypes(Enum):
    INDETERMINATE = 'INDETERMINATE'
    LICENSE_END = 'LICENSE_END'
    LICENSE_CHANGE = 'LICENSE_CHANGE'
    DESIGNATION_END = 'DESIGNATION_END'
    REINCORPORATION = 'REINCORPORATION'
    

class PersonalLeaveLicense(Base):

    __tablename__ = 'personal_leave_licenses'

    user_id = Column(String)
    license_id = Column(String, ForeignKey('personal_leave_licenses.id'))

    type = Column(SQLEnum(LicenseTypes))

    start = Column(Date)
    end = Column(Date)
    end_type = Column(SQLEnum(LicenseEndTypes))

    historic = Boolean

    exp = Column(String)
    res = Column(String)
    cor = Column(String)

    comments = Column(String)


class DesignationLeaveLicense(Base):

    __tablename__ = 'designation_leave_licenses'

    designation_id = Column(String, ForeignKey('designations.id'))
    designation = relationship('Designation', foreign_keys=[designation_id])    

    license_id = Column(String, ForeignKey('designation_leave_licenses.id'))

    start = Column(Date)
    end = Column(Date)

    historic = Boolean

    exp = Column(String)
    res = Column(String)
    cor = Column(String)

    type = Column(SQLEnum(LicenseTypes))

    comments = Column(String)