import StringIO
import time


class BufferLog(object):

    def _log(self, msg):
        print msg

    info = _log
    debug = _log
    error = _log


logger = BufferLog()

