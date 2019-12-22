import sys
import psycopg2

places = []

dsn = sys.argv[1]
con = psycopg2.connect(dsn=dsn)
try:
    cur = con.cursor()
    try:
        cur.execute("select catxmat_id as id, m.materia_nombre || ' - ' || c.catedra_nombre  as nombre from catedras_x_materia cm left join materia m on (m.materia_id = cm.catxmat_materia_id) left join catedra c on (cm.catxmat_catedra_id = c.catedra_id)")
        for p in cur:
            places.append({
                'i':p[0],
                'n':p[1]
            })
            
    finally:
        cur.close()
finally:
    con.close()


from sileg_model.model.entities.Place import Place, PlaceTypes
from sileg_model.model import open_session
from sileg_model.model.SilegModel import SilegModel

silegModel = SilegModel()
with open_session() as session:
    try:
        for p in places:
            name = p['n']
            ps = silegModel.get_places_by_name(session, name)
            if not ps or len(ps) <= 0:
                print(f"agregando lugar : {name}")
                place = Place()
                place.name = name
                place.type = PlaceTypes.CATEDRA
                session.add(place)
                session.commit()

    except Exception as e:
        print(e)