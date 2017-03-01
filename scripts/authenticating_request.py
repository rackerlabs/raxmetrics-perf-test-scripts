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
        token = self.user.get_token()
        headers.append(NVPair("X-Auth-Token", token))

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

    def execute_request(self, request_method, headers_arg_index, args, kwargs):
        args1, kwargs1 = self.authenticate(args, kwargs, headers_arg_index)
        response = request_method(*args1, **kwargs1)
        if response.getStatusCode() in [401, 403]:
            self.user.reauthenticate()
            args2, kwargs2 = self.authenticate(args, kwargs, headers_arg_index)
            response = request_method(*args2, **kwargs2)
        return response

    def GET(self, *args, **kwargs):
        return self.execute_request(self.request.GET, 2, args, kwargs)

    def HEAD(self, *args, **kwargs):
        return self.execute_request(self.request.HEAD, 2, args, kwargs)

    def POST(self, *args, **kwargs):
        return self.execute_request(self.request.POST, 2, args, kwargs)

    def PUT(self, *args, **kwargs):
        return self.execute_request(self.request.PUT, 2, args, kwargs)

    def DELETE(self, *args, **kwargs):
        return self.execute_request(self.request.DELETE, 1, args, kwargs)

    def OPTIONS(self, *args, **kwargs):
        return self.execute_request(self.request.OPTIONS, 2, args, kwargs)

    def TRACE(self, *args, **kwargs):
        return self.execute_request(self.request.TRACE, 1, args, kwargs)


class NullAuthenticatingRequest(AuthenticatingRequest):
    def __init__(self, request):
        super(NullAuthenticatingRequest, self).__init__(request)

    def authenticate(self, args, kwargs, headers_arg_index):
        return args, kwargs
