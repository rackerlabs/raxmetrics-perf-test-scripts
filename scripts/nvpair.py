#!/usr/bin/env python


class NVPair(object):
    """
    Normally, one would import the NVPair class from Grinder's HTTPClient
    module. However, when trying to run the tests in an IDE or under python
    (not jython), HTTPClient is unavailable. In those situations, this class
    can serve as a simple stand-in.
    """

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def getName(self):
        return self.name

    def getValue(self):
        return self.value
