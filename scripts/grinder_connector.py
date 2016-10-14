
from net.grinder.plugin.http import HTTPRequest
from com.xhaus.jyson import JysonCodec as json

class ResponseWrapper(object):
    def __init__(self, response):
        self.response = response

    def json(self):
        return json.loads(self.response.getText())


class GrinderConnector(object):
    def __init__(self):
        self.request = HTTPRequest()

    def post(self, url, body, headers, *args, **kwargs):
        body = str(json.dumps(body))
        return ResponseWrapper(self.request.POST(url, body, headers))