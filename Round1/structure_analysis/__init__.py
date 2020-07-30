import collections
import os
import sys

def get_feature_dict(filename, ignore_indent=False):
    lines = open(os.path.join(filename, 'Structure_Info.txt'), 'r')
    kv = collections.defaultdict(lambda: [0., 0., float('inf'), 0.])
    ret = collections.defaultdict(float)
    for l in lines:
        if len(l.strip()) == 0:
            continue
        if l[0] == '-' or l.lstrip()[0] == '[':
            # new context
            if ignore_indent:
                name = l.strip()
            else:
                name = l.rstrip()
        else:
            try:
                # kv pair
                k, v = l.split(': ')
                k = k.lstrip()
                v = v.strip()
                if k[:2] == '0x':
                    # memory line
                    k = k.split(' ')[-1]
                if k == 'Name':
                    # section name
                    name += ':' + v
                    continue
                try:
                    # numerical value
                    if v[:2] == '0x':
                        # hex numbers
                        u = ''
                        for c in v[2:]:
                            if c not in '0123456789abcdefABCDEF':
                                break
                            u += c
                        val = float(int(u, 16))
                    else:
                        # entropy and possibly other floats
                        val = float(v.split(' ')[0])
                    arr = kv[name + ':' + k]
                    arr[0] += 1                 # ctr
                    arr[1] += val               # sum
                    arr[2] = min(arr[2], val)   # min
                    arr[3] = max(arr[3], val)   # max
                except:
                    # non-numerical values
                    if v.find(', ') != -1:
                        # list of flags, or such
                        for x in v.split(', '):
                            ret[curr + ':' + k + ':' + x] = 1.
                    # else value is string, eg. hash
            except:
                # non-kv lines
                if l.find('dll') != -1:
                    # dll line
                    ret[name + ':' + l.split('.')[0] + '.dll'] += 1.
    for k, arr in kv.items():
        ret[k + ':ctr'] = arr[0]
        ret[k + ':mean'] = arr[1] / max(1, arr[0])
        if arr[0] > 1:
            ret[k + ':min'] = arr[2]
            ret[k + ':max'] = arr[3]
    return ret

if __name__ == '__main__':
    if sys.argv[1] == '-n':
        for k, v in get_feature_dict(sys.argv[2], True).items():
            print(k, ':', v)
    else:
        for k, v in get_feature_dict(sys.argv[1]).items():
            print(k, ':', v)
