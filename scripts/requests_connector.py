
import requests


class RequestsConnector(object):
    def post(self, url, body, headers, *args, **kwargs):
        return requests.post(url, json=body, headers=headers, *args, **kwargs)
