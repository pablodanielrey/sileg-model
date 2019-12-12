
class UsersAPI:

    def __init__(self, api_url, api):
        self.url = api_url
        self.api = api

    def _get_all_uids(self, token=None):
        query = '{}/usuarios/uids'.format(self.url)
        r = self.api.get(query, token=token)
        if not r.ok:
            return None
        usr = r.json()
        return usr

    def _get_user_uuid(self, uuid, token=None):
        query = '{}/usuarios/{}'.format(self.url, uuid)
        r = self.api.get(query, token=token)
        if not r.ok:
            return None
        usr = r.json()
        if len(usr) > 0:
            return usr[0]
        return None

    def _get_users_uuid(self, uuids=[], token=None):
        uids = '+'.join(uuids)
        query = '{}/usuarios/{}'.format(self.url, uids)
        r = self.api.get(query, token=token)
        if not r.ok:
            return None
        usrs = r.json()        
        return usrs

    def _get_user_dni(self, dni, token=None):
        query = '{}/usuario_por_dni/{}'.format(self.url, dni)
        r = self.api.get(query, token=token)
        if not r.ok:
            return None
        return r.json()

    def _search_user(self, search, token=None):
        params = {
            'q':search
        }
        query = '{}/usuario'.format(self.url)
        r = self.api.get(query, params=params, token=token)
        if not r.ok:
            return None
        for usr in r.json():
            return usr        
        return None

    def _search_user(self, search, token=None):
        params = {
            'q':search
        }
        query = '{}/usuarios'.format(self.url)
        r = self.api.get(query, params=params, token=token)
        if not r.ok:
            return []
        users = r.json()
        return users