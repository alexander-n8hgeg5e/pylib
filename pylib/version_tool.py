from binascii import hexlify,unhexlify

def str2int(hexstr,encoding='utf-8'):
    return int(hexlify(hexstr.encode(encoding=encoding)).decode(encoding=encoding),base=16)

def int2str(i,encoding='utf-8'):
    hexstr=hex(i)[2:]
    return unhexlify(hexstr).decode(encoding=encoding)

def gh2ver(hashstr,length):
    prefix_decimal=str(str2int("gh"+str(length)))
    if not type(hashstr) is str or not len(hashstr) >= length:
        raise Exception("ERROR: hash is too short")
    hashstr=hashstr[:length]
    dec_hash=str(str2int(hashstr))
    return prefix_decimal+"."+dec_hash

def ver2gh(verstr,length):
    prefix_need=str(str2int("gh"+str(length)))
    prefix_is,intstr=verstr.split(".")
    if prefix_need != prefix_is:
        raise Exception('ERROR: gh'+str(length)+'version numbers start with "'+prefix_decimal+'", .\n'
                        'The supplied one does not.')
    return int2str(int(intstr))

