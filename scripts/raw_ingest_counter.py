
class RawIngestCounter():

    class Target():
        def target(self):
            pass

    def __init__(self, test):
        self.target = self.Target()
        test.record(self.target)

    def count(self, n=1):
        for i in xrange(n):
            self.target.target()


class NullIngestCounter():
    def __init__(self, test=None):
        pass

    def count(self, n=1):
        pass
