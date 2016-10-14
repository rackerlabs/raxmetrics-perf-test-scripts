
from connector import Connector


class User(object):

    token = None
    tenant_id = None

    def __init__(self, auth_url, username, api_key, conn=None):

        if conn is None:
            conn = Connector()

        self.auth_url = auth_url
        self.username = username
        self.api_key = api_key
        self.connector = conn

    def _get_data(self):
        request_body = {
            "auth": {
                "RAX-KSKEY:apiKeyCredentials": {
                    "username": self.username,
                    "apiKey": self.api_key}}}
        headers = {
            "Accept": "application/json",
            "Content-type": "application/json"
        }
        resp = self.connector.post(self.auth_url, request_body, headers)
        catalog = resp.json()
        self.tenant_id = catalog['access']['token']['tenant']['id']
        self.token = catalog['access']['token']['id']
        return self.tenant_id, self.token

    def get_token(self):
        if self.token is None:
            self._get_data()
        return self.token

    def get_tenant_id(self):
        if self.tenant_id is None:
            self._get_data()
        return self.tenant_id


class NullUser(object):
    def get_token(self):
        return 'token'

    def get_tenant_id(self):
        return 'tenantId'
