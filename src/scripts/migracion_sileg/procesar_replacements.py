
from sileg_model.model import open_session
from sileg_model.model.SilegModel import SilegModel
from sileg_model.model.entities.Designation import DesignationLabel, Designation, DesignationTypes, DesignationEndTypes

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

            """
                ///////////////////////////////////
                en el caso de que en el sileg viejo reempa signifique que es la designación a reemplazar
                ///////////////////////////////////
            """

            ''' busco la designacion que en el sileg viejo tenia id rep_id '''
            replaced_did = _sileg_viejo_id_to_uuid(session, rep_id)

            ''' busco la desigancion a ser actualizada '''
            replacement = session.query(Designation).filter(Designation.id == did).one()
            replacement.designation_id = replaced_did
            replacement.type = DesignationTypes.REPLACEMENT
            replacement.end_type = DesignationEndTypes.REPLACEMENT


            """ 
                ////////////////////////////////////////
                en el caso de que en el sileg viejo reempa signifique que es la designacion que reemplaza a esta original
                ////////////////////////////////////////
            """

            """
            ''' busco la designacion que en el sileg viejo tenia id rep_id '''
            replacement_did = _sileg_viejo_id_to_uuid(session, rep_id)

            ''' busco la designacion que en debe ser actualizada '''
            replacement = session.query(Designation).filter(Designation.id == replacement_did).one()
            replacement.designation_id = did
            replacement.type = DesignationTypes.REPLACEMENT
            replacement.end_type = DesignationEndTypes.REPLACEMENT

            """
            """
                ///////////////////////////////////////////
            """

            session.commit()
