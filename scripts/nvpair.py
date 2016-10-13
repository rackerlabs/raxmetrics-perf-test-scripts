#!/usr/bin/env python


def NVPair(*args):
    """
    Normally, one would import the NVPair class from Grinder's HTTPClient
    module. However, when trying to run the tests in an IDE or under python
    (not jython), HTTPClient is unavailable. In those situations, this function
    can serve as a simple stand-in.
    """
    return tuple(args)
