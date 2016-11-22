#!/usr/bin/env python

from http_failure_exception import HttpFailureException


class ResponseCheckingRequest():
    def __init__(self, request):
        self.request = request

    def check(self, response):
        if not (200 <= response.getStatusCode() < 300):
            raise HttpFailureException(response)
        return response

    def GET(self, *args, **kwargs):
        return self.check(self.request.GET(*args, **kwargs))

    def HEAD(self, *args, **kwargs):
        return self.check(self.request.HEAD(*args, **kwargs))

    def POST(self, *args, **kwargs):
        return self.check(self.request.POST(*args, **kwargs))

    def PUT(self, *args, **kwargs):
        return self.check(self.request.PUT(*args, **kwargs))

    def DELETE(self, *args, **kwargs):
        return self.check(self.request.DELETE(*args, **kwargs))

    def OPTIONS(self, *args, **kwargs):
        return self.check(self.request.OPTIONS(*args, **kwargs))

    def TRACE(self, *args, **kwargs):
        return self.check(self.request.TRACE(*args, **kwargs))
