#!/usr/bin/env python

import ast


def convert(s):
    try:
        return int(s)
    except:
        pass
    if isinstance(s, basestring):
        if s[0] in ("'", '"'):
            return ast.literal_eval(s)
        return s
    return str(s)


def from_config_file(cfg):
    cfg2 = {}
    for k, v in cfg.iteritems():
        if str(v).startswith(".."):
            continue
        if not k.startswith("grinder.bf."):
            continue
        k = k.replace("grinder.bf.", "")
        cfg2[k] = convert(v)
    return cfg2
