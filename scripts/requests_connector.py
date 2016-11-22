
import requests


class RequestsConnector(object):
    """A connector that makes HTTP requests via the `requests` library. This is
    used in tests of the `user.User` class.
    """

    def post(self, url, body, headers, *args, **kwargs):
        return requests.post(url, json=body, headers=headers, *args, **kwargs)
