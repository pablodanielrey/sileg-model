import os
import psycopg2
import psycopg2.extras


class DbaAdscriptos:

    host = os.environ['ADSCRIPTOS_DB_HOST']
    dbname = os.environ['ADSCRIPTOS_DB_NAME']
    user = os.environ['ADSCRIPTOS_DB_USER']
    password = os.environ['ADSCRIPTOS_DB_PASSWORD']
    

    @classmethod
    def periodos(cls):
      conn = psycopg2.connect(host=cls.host, dbname=cls.dbname, user=cls.user, password=cls.password)
      try:
          cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
          try:
              cur.execute('''
                SELECT pri.id, fecha_desde, fecha_hasta, estado, notas, fecha_baja, nombres, apellidos, documento_numero, descripcion, dep.nombre
                FROM v4.periodo pri
                INNER JOIN v4.adscripcion ads ON (pri.adscripcion = ads.id)
                INNER JOIN v4.persona per ON (ads.alumno = per.id)
                INNER JOIN v4.catedra cat ON (ads.catedra = cat.id)
                INNER JOIN v4.departamento dep ON (cat.departamento = dep.id);
              ''');

              return cur.fetchall()
          finally:
            cur.close()

      finally:
          conn.close()
        
        
        
if __name__ == '__main__':
  rows = DbaAdscriptos.periodos();
  with open('adscripciones.csv', 'w', newline='') as csvfile:
  
    csvw = csv.writer(csvfile, delimiter=',', quotechar='\"', quoting=csv.QUOTE_NONNUMERIC)
    csvw.writerow(["id", "desde", "hasta", "estado", "notas", "baja", "nombres", "apellidos", "DNI", "catedra", "departamento"])
    for row in rows:
      csvw.writerow(row)
  return "se ha creado el archivo adscripciones.csv"
        
   
        
