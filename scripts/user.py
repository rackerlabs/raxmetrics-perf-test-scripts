
import requests
import json


class User(object):

    token = None
    tenant_id = None

    def __init__(self, auth_url, username, api_key, connector=None):

        if connector is None:
            connector = requests

        self.auth_url = auth_url
        self.username = username
        self.api_key = api_key
        self.connector = connector

    def _get_data(self):
        template = '{"auth":{ "RAX-KSKEY:apiKeyCredentials":{' \
                   '"username":"%s","apiKey":"%s"}}}'
        request_body = json.loads(template % (self.username, self.api_key))
        headers = {
            "Accept": "application/json",
            "Content-type": "application/json"
        }
        resp = self.connector.post(self.auth_url, json=request_body,
                                   headers=headers)
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
