

class ErrorLoggingRequest():

    """This request write to the grinder log all error responses with a
    status code of 5XX."""

    def __init__(self, request, log):
        self.request = request
        self.log = log

    def wrap(self, callee):
        response = callee()
        if response.getStatusCode() >= 500:
            s = '\n    %s %s %s\n' % (response.getVersion(),
                                      response.getStatusCode(),
                                      response.getReasonLine())

            def clean(s):
                return s.replace('\n', '\n    ')
            for header in response.listHeaders():
                s += '    %s: %s\n' % (header,
                                       clean(response.getHeader(header)))
            text = response.getText()
            if text:
                s += '\n    '
                s += clean(text)
            self.log(s)
        return response

    def GET(self, *args, **kwargs):
        return self.wrap(lambda: self.request.GET(*args, **kwargs))

    def HEAD(self, *args, **kwargs):
        return self.wrap(lambda: self.request.HEAD(*args, **kwargs))

    def POST(self, *args, **kwargs):
        return self.wrap(lambda: self.request.POST(*args, **kwargs))

    def PUT(self, *args, **kwargs):
        return self.wrap(lambda: self.request.PUT(*args, **kwargs))

    def DELETE(self, *args, **kwargs):
        return self.wrap(lambda: self.request.DELETE(*args, **kwargs))

    def OPTIONS(self, *args, **kwargs):
        return self.wrap(lambda: self.request.OPTIONS(*args, **kwargs))

    def TRACE(self, *args, **kwargs):
        return self.wrap(lambda: self.request.TRACE(*args, **kwargs))
