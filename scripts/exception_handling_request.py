
from http_failure_exception import HttpFailureException


class ExceptionHandlingRequest():

    """This class catches exceptions thrown by the wrapped request object,
     namely a ResponseCheckingRequest instance. That way, if there is an HTTP
     error, it gets counted in the grinder statistics, but the exception
     stacktrace doesn't clutter up the grinder logs."""

    def __init__(self, request):
        self.request = request

    def wrap(self, callee):
        try:
            return callee()
        except HttpFailureException as e:
            return e.response

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
