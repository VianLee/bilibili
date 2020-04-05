__all__ = ('debug', 'bv2av', 'av2bv')



import sys



table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
tr = dict(map(reversed, enumerate(table)))
s = [11, 10, 3, 8, 4, 6]
xor = 177451812
add = 8728348608



def debug(**kwargs):
    import IPython
    IPython.embed(user_ns=sys._getframe(1).f_locals, colors='Linux', **kwargs)


def bv2av(x, prefix=True):
    '''
    Example:
        >>> bv2av('BV1A7411w71V')
        'av90501130'
    '''
    r = sum(tr[x[s[i]]]*58**i for i in range(6))
    id = (r-add) ^ xor
    return f'av{id}' if prefix else str(id)


def av2bv(x):
    '''
    Example:
        >>> av2bv('AV90501130')
        'BV1A7411w71V'
    '''
    x = int(str(x).replace('av', '').replace('AV', ''))
    x = (x^xor) + add
    r = list('BV1  4 1 7  ')
    for i in range(6):
        r[s[i]] = table[x//58**i%58]
    return ''.join(r)
