# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time


class TimeRange(object):
    def __init__(self, start_time=None, end_time=None):
        def parse_time(t):
            try:
                _time = time.mktime(time.strptime(t, "%Y%m%d"))
                return unicode(_time)
            except Exception:
                return "0"

        self.start_time = parse_time(start_time)
        self.end_time = parse_time(end_time)
        if self.end_time == "0":
            self.end_time = unicode(time.time())
