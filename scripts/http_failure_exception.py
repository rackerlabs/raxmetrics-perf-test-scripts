
class HttpFailureException(Exception):

    response = None

    def __init__(self, response):
        super(HttpFailureException, self).__init__(
            self,
            'The HTTP request did not succeed. Response code %s' %
            response.getStatusCode())
        self.response = response
