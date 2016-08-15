#!/usr/bin/env python

import ast


def convert(s):
    try:
        return int(s)
    except:
        pass
    if isinstance(s, basestring):
        if len(s) > 0 and s[0] in ("'", '"'):
            return ast.literal_eval(s)
        return s
    return str(s)


def clean_configs(cfg):
    cfg2 = {}
    for k, v in cfg.iteritems():
        if k.startswith("grinder.bf."):
            k = k.replace("grinder.bf.", "")
        cfg2[k] = convert(v)
    return cfg2
