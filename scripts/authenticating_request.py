#!/usr/bin/env python

try:
    from HTTPClient import NVPair
except ImportError:
    from nvpair import NVPair


class AuthenticatingRequest(object):
    def __init__(self, request, user):
        self.request = request
        self.user = user

    def authenticate(self, args, kwargs, headers_arg_index):

        # first, look for the headers argument in args. if it's not there, look
        # in kwargs by name
        by_kwargs = False
        headers = None
        if args and len(args) > headers_arg_index:
            headers = args[headers_arg_index]
        elif 'headers' in kwargs:
            headers = kwargs['headers']
            by_kwargs = True

        # normalize to a list
        if not headers:
            headers = []
        if isinstance(headers, tuple):
            headers = [h for h in headers]

        # add the token header
        headers.append(NVPair("X-Auth-Token", self.user.get_token()))

        # update args and kwargs, as necessary
        if by_kwargs:
            kwargs['headers'] = headers
        else:
            # The headers_arg_index'th arg should contain the headers.
            # It varies for different http methods.
            # See http://grinder.sourceforge.net/g3/script-javadoc/net/grinder/plugin/http/HTTPRequest.html
            if not args:
                args = [None] * (headers_arg_index + 1)
            if isinstance(args, tuple):
                args = [a for a in args]
            while len(args) < (headers_arg_index + 1):
                args.append(None)
            args[headers_arg_index] = headers

        return args, kwargs

    def GET(self, *args, **kwargs):
        args, kwargs = self.authenticate(args, kwargs, 2)
        return self.request.GET(*args, **kwargs)

    def HEAD(self, *args, **kwargs):
        args, kwargs = self.authenticate(args, kwargs, 2)
        return self.request.HEAD(*args, **kwargs)

    def POST(self, *args, **kwargs):
        args, kwargs = self.authenticate(args, kwargs, 2)
        return self.request.POST(*args, **kwargs)

    def PUT(self, *args, **kwargs):
        args, kwargs = self.authenticate(args, kwargs, 2)
        return self.request.PUT(*args, **kwargs)

    def DELETE(self, *args, **kwargs):
        args, kwargs = self.authenticate(args, kwargs, 1)
        return self.request.DELETE(*args, **kwargs)

    def OPTIONS(self, *args, **kwargs):
        args, kwargs = self.authenticate(args, kwargs, 2)
        return self.request.OPTIONS(*args, **kwargs)

    def TRACE(self, *args, **kwargs):
        args, kwargs = self.authenticate(args, kwargs, 1)
        return self.request.TRACE(*args, **kwargs)


class NullAuthenticatingRequest(AuthenticatingRequest):
    def __init__(self, request):
        super(NullAuthenticatingRequest, self).__init__(request)

    def authenticate(self, args, kwargs, headers_arg_index):
        return args, kwargs
