#!/usr/bin/env python

import java.lang.Class

def dict_from_properties(p):
    d = {}
    for entry in p.entrySet():
        d[entry.key] = entry.value
    return d


def is_java_object(obj):
    if type(type(obj)) == java.lang.Class:
        return True
    return False

