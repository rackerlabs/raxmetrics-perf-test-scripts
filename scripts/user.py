
import datetime
import email.utils
import threading
import time

from connector import Connector

try:
    from HTTPClient import NVPair
except ImportError:
    from nvpair import NVPair


class User(object):

    token = None
    tenant_id = None
    logger = None

    def __init__(self, auth_url, username, api_key, conn=None):

        if conn is None:
            conn = Connector()

        self.auth_url = auth_url
        self.username = username
        self.api_key = api_key
        self.connector = conn
        self.lock = threading.RLock()

    def _get_data(self):
        def get_data_sync():
            request_body = {
                "auth": {
                    "RAX-KSKEY:apiKeyCredentials": {
                        "username": self.username,
                        "apiKey": self.api_key}}}
            headers = [
                NVPair("Accept", "application/json"),
                NVPair("Content-type", "application/json")
            ]
            for retries in xrange(3):
                resp = self.connector.post(self.auth_url, request_body,
                                           headers)
                if 200 <= resp.status_code < 300:
                    break
                if resp.status_code in [413, 429]:
                    try:
                        # TODO: lower/upper case
                        retry_after = resp.headers.get('Retry-After')
                        if retry_after:
                            # TODO: double-check time zone
                            after = email.utils.parsedate(retry_after)
                            now = datetime.datetime.utcnow()
                            delta = (after - now).total_seconds()
                            if delta > 0:
                                if self.logger:
                                    self.logger("Got status code %s, will "
                                                "retry" %
                                                resp.status_code)
                                time.sleep(delta)
                    except:
                        if self.logger:
                            self.logger("Got status code %s, can't retry" %
                                        resp.status_code)
                        return (None, None)
                else:
                    if self.logger:
                        self.logger("Got status code %s, won't retry" %
                                    resp.status_code)
                    return (None, None)
            else:
                if self.logger:
                    self.logger("Couldn't get token and tenant")
                return (None, None)

            catalog = resp.json()
            self.tenant_id = catalog['access']['token']['tenant']['id']
            self.token = catalog['access']['token']['id']
            return self.tenant_id, self.token

        self.lock.acquire()
        try:
            if self.token is None or self.tenant_id is None:
                return get_data_sync()
        finally:
            self.lock.release()
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
