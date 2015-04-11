import StringIO
import time


class BufferLog(object):

    def __init__(self, interval=1):
        self._buf = StringIO.StringIO()
        self._interval = interval
        self._last = time.time()
        self._everage_sum = 0.0
        self._everage_times = 0.0


    def _log(self, msg):
        timestamp = time.time()
        self._buf.write("%f - %s\n" % (timestamp, msg))
        if timestamp - self._last > self._interval:
            print self._buf.buf
            self._buf.buf = ""
            self._last = timestamp

    def everage(self, msg, value):
        self._everage_sum += value
        self._everage_times += 1.0
        timestamp = time.time()
        if timestamp - self._last > self._interval:
            print msg, self._everage_sum/self._everage_times, self._everage_times
            self._everage_times = 0.0
            self._everage_sum = 0.0
            self._last = timestamp

    info = _log
    debug = _log
    error = _log


logger = BufferLog()

