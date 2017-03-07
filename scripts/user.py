
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
    expires = None

    def __init__(self, auth_url, username, api_key, config, conn=None):

        if conn is None:
            conn = Connector()

        self.auth_url = auth_url
        self.username = username
        self.api_key = api_key
        self.config = config
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
                        # https://jira.rax.io/browse/CMD-1449
                        retry_after = resp.headers.get('Retry-After')
                        if retry_after:
                            # TODO: double-check time zone
                            # https://jira.rax.io/browse/CMD-1449
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
            expiration_date = catalog['access']['token']['expires']
            try:
                self.expires = datetime.datetime.strptime(expiration_date,
                                                          "%Y-%m-%dT%H:%M:%S.%fZ")
            except:
                parts = expiration_date.split('.')
                dt = datetime.datetime.strptime(parts[0], "%Y-%m-%dT%H:%M:%S")
                if len(parts) > 1:
                    microseconds = parts[1]
                    if microseconds.endswith('Z'):
                        microseconds = microseconds[0:-1]
                    dt = dt.replace(microsecond=int(microseconds))
                self.expires = dt
                pass
            return self.tenant_id, self.token

        self.lock.acquire()
        try:
            return get_data_sync()
        finally:
            self.lock.release()

    def get_token(self):
        if self.token is None:
            self._get_data()
        return self.token

    def get_tenant_id(self):
        if self.tenant_id is None:
            self._get_data()
        return self.tenant_id

    def reauthenticate(self):
        self.token = None
        self.tenant_id = None
        self.expires = None
        return self._get_data()

    def is_expired(self, current_time=None):
        if current_time is None:
            current_time = datetime.datetime.utcnow()

        if not self.expires:
            return False

        if current_time >= self.expires:
            return True

        return False


class NullUser(object):
    def get_token(self):
        return 'token'

    def get_tenant_id(self):
        return 'tenantId'

    def reauthenticate(self):
        return self.get_tenant_id(), self.get_token()
