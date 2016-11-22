
from net.grinder.plugin.http import HTTPRequest
from com.xhaus.jyson import JysonCodec as json


class ResponseWrapper(object):

    """A wrapper class to make `HTTPClient.HTTPResponse` act more like a
    `requests.Response`, for interoperability.
    """

    def __init__(self, response):
        self.response = response

    @property
    def status_code(self):
        return self.response.getStatusCode()

    @property
    def headers(self):
        return dict([(name, self.response.getHeader(name))
                     for name in self.response.listHeaders()])

    @property
    def body(self):
        return self.response.getText()

    def json(self):
        return json.loads(self.response.getText())


class GrinderConnector(object):

    """A connector that makes HTTP requests via The Grinder's worker thread.
    This is used by the `user.User` class to authenticate.
    """

    def __init__(self):
        self.request = HTTPRequest()

    def post(self, url, body, headers, *args, **kwargs):
        url = str(url)
        body = str(json.dumps(body))
        resp = self.request.POST(url, body, headers)
        return ResponseWrapper(resp)
