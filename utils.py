class dotdict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def flatten(items):
    ret = []
    for item in items:
        if type(item) in {list, tuple}: ret += flatten(item)
        else: ret += [item]
    return ret

class Error(Exception):
    pass

def error(msg: str=None):
    if not msg: raise Error()
    raise Error(f"msg")

def get_indent(line):
    if '\t' in line: error(f"{line} uses tab indent, which currently is not supported")
    if not line: indent = 0
    else:
        i = 0
        while i < len(line) and line[i] == ' ':
            i += 1
        indent = i
    return indent
