#!/usr/bin/env python


class ThrottlingRequest(object):
    def __init__(self, tgroup, request):
        self.tgroup = tgroup
        self.request = request

    def count_request(self):
        self.tgroup.count_request()

    def GET(self, *args, **kwargs):
        self.count_request()
        return self.request.GET(*args, **kwargs)

    def HEAD(self, *args, **kwargs):
        self.count_request()
        return self.request.HEAD(*args, **kwargs)

    def POST(self, *args, **kwargs):
        self.count_request()
        return self.request.POST(*args, **kwargs)

    def PUT(self, *args, **kwargs):
        self.count_request()
        return self.request.PUT(*args, **kwargs)

    def DELETE(self, *args, **kwargs):
        self.count_request()
        return self.request.DELETE(*args, **kwargs)

    def OPTIONS(self, *args, **kwargs):
        self.count_request()
        return self.request.OPTIONS(*args, **kwargs)

    def TRACE(self, *args, **kwargs):
        self.count_request()
        return self.request.TRACE(*args, **kwargs)
