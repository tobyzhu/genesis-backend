
# coding=utf-8

import zlib,gzip

def str2hex(s):
    return binascii.hexlify(bytes(str.encode(s)))


def hex2str(h):
    return binascii.unhexlify(h)

hexstring = input()
if len(hexstring) > 200:
    hexstring = str(zlib.compress(hexstring.encode('utf-8')))
    print(hexstring)
hexstring = str2hex(hexstring)
ph = str(hexstring.decode('utf-8'))
print(ph)

#decompressing text
unhexsring = hex2str(hexstring).decode('utf8')
if 'x' in str(unhexsring):
    print('compressed')
    unhexsring = str(zlib.decompress(unhexsring).encode('utf8'))
print(unhexsring)
# bytes a='12345'
s_compress(bytes('HBsjzyfy','gbk'))
