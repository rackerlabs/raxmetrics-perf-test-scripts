#!/usr/bin/env python

import java.lang.Class
import java.util.Properties
from net.grinder.script.Grinder import ScriptContext
import net.grinder.engine.process.ScriptContextImplementation


def dict_from_properties(p):
    d = {}
    for entry in p.entrySet():
        d[entry.key] = p.getProperty(entry.key)
    return d


def is_java_object(obj):
    if type(type(obj)) == java.lang.Class:
        return True
    return False


def get_config_from_grinder(grinder):
    if is_java_object(grinder):
        if isinstance(grinder, ScriptContext):
            config = dict_from_properties(grinder.getProperties())
        elif type(grinder) == \
                net.grinder.engine.process.ScriptContextImplementation:
            config = dict_from_properties(grinder.getProperties())
        elif isinstance(grinder, java.lang.Properties):
            config = dict_from_properties(grinder)
        else:
            raise TypeError("Unknown configuration object type")
    else:
        config = grinder
    return config
