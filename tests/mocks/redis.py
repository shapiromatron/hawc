from collections import deque


class RedisMock:
    """A simplified redis queue mock designed with array operations.

    Designed for operations used in `common.diagnostics.WorkerHealthcheck` and dramatically
    simplified; not a more generalized mock object.
    """

    MAX_SIZE = 5

    def __init__(self):
        self.data = {}

    def delete(self, key):
        del self.data[key]

    def pipeline(self):
        return self

    def execute(self):
        pass

    def lpush(self, key, value):
        if key not in self.data:
            self.data[key] = deque(maxlen=self.MAX_SIZE)
        self.data[key].appendleft(str(value).encode())

    def ltrim(self, key, start, end):
        if key not in self.data:
            return None
        values = list(self.data[key])[start : end + 1]
        self.data[key] = deque(values, maxlen=self.MAX_SIZE)

    def lindex(self, key, i):
        try:
            return self.data[key][i]
        except (KeyError, IndexError):
            return None

    def lrange(self, key, *args):
        if key not in self.data:
            return []
        return list(self.data[key])
