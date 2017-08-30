#!/usr/bin/env python
# -*- coding: latin-1 -*-
#


def check_calls(self, calls, values):
    self.assertEqual(len(calls), len(values))

    r = {}
    for call in calls:
        name = call[0][0]
        value = call[0][1]
        r[name] = value

    for name, value in values:
        self.assertEqual(r.pop(name), value)

    self.assertEqual(len(r), 0)
