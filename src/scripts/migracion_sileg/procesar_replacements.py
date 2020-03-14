
from sileg_model.model import open_session
from sileg_model.model.SilegModel import SilegModel
from sileg_model.model.entities.Designation import DesignationLabel, Designation

def _sileg_viejo_id_to_uuid(session, did):
    rid = session.query(DesignationLabel.designation_id).filter(DesignationLabel.name == 'sileg_viejo_id', DesignationLabel.value == did).one()
    return rid

if __name__ == '__main__':

    with open_session() as session:
        
        ''' obtengo todas las designaciones que son reemplazos '''
        labels = session.query(DesignationLabel).filter(DesignationLabel.name == 'sileg_viejo_replacement').all()
        for label in labels:
            
            did = label.designation_id
            rep_id = label.value

            ''' busco la designacion que en el sileg viejo tenia id rep_id '''
            replaced_did = _sileg_viejo_id_to_uuid(session, rep_id)

            ''' busco la designacion que en debe ser actualizada '''
            designation = session.query(Designation).filter(Designation.id == did).one()
            designation.designation_id = replaced_did
            
            session.commit()
