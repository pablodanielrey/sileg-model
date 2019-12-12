'''
    https://developers.google.com/admin-sdk/directory/
    https://developers.google.com/admin-sdk/directory/v1/reference/users/

    aca estan los scopes
    https://developers.google.com/identity/protocols/googlescopes
'''

import os

from apiclient import discovery, errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.service_account import ServiceAccountCredentials
import httplib2

class GAuthApis:

    adminGoogle = os.environ['ADMIN_USER_GOOGLE']

    SCOPES = 'https://www.googleapis.com/auth/admin.directory.user'

    SCOPESGMAIL = [
        'https://mail.google.com/',
        'https://www.googleapis.com/auth/gmail.settings.sharing'
    ]


    SCOPESDRIVE = ['https://www.googleapis.com/auth/spreadsheets',
              'https://www.googleapis.com/auth/drive']


    @classmethod
    def getCredentials(cls, username, SCOPES=SCOPES):
        ''' genera las credenciales delegadas al usuario username '''
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,'credentials.json')

        credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_path, SCOPES)

        ''' uso una cuenta de admin del dominio para acceder a todas las apis '''
        admin_credentials = credentials.create_delegated(username)

        return admin_credentials

    @classmethod
    def getServiceAdmin(cls, username=adminGoogle, version='directory_v1'):
        api='admin'
        ''' crea un servicio de acceso a las apis y lo retora '''
        credentials = cls.getCredentials(username, cls.SCOPES)
        http = credentials.authorize(httplib2.Http())
        service = discovery.build(api, version, http=http)
        return service

    @classmethod
    def getServiceSheet(cls, username=adminGoogle, version='v4'):
        api='sheets'
        ''' crea un servicio de acceso a las apis y lo retora '''
        credentials = cls.getCredentials(username, cls.SCOPESDRIVE)
        http = credentials.authorize(httplib2.Http())
        service = discovery.build(api, version, http=http)
        return service


    @classmethod
    def getServiceGmail(cls, username=adminGoogle, version='v1'):
        api='gmail'
        ''' crea un servicio de acceso a las apis y lo retora '''
        credentials = cls.getCredentials(username, cls.SCOPESGMAIL)
        http = credentials.authorize(httplib2.Http())
        service = discovery.build(api, version, http=http)
        return service
