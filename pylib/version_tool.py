from binascii import hexlify,unhexlify

__doc__="""
The version tools functions are made for
converting githashes to 
gentoo (valid)* version numbers
the conversion can be made lossless
by specifying a lenght parameter that
is the character lenght of the hash.
The keyword "gh" ( means githash )
and the length used for encoding is
encoded in the part befor the dot.

*: if not to long length parameter is choosen.
Because the base 16 hex encoding will be a base 10,
the characterlength will be more than the
githash.
"""
def str2int(hexstr,encoding='utf-8'):
    """
    Encodes string that is encodable with encoding,
    to a decimal number.
    The data is fully restoreable
    if the encoding is known and are in the encodings range.
    It's like with storing any string.
    """
    return int(hexlify(hexstr.encode(encoding=encoding)).decode(encoding=encoding),base=16)

def int2str(i,encoding='utf-8'):
    """
    Reverses the functionality of the function str2int.
    """
    hexstr=hex(i)[2:]
    return unhexlify(hexstr).decode(encoding=encoding)

def gh2ver(hashstr,length):
    """
    Converts git-hash to gentoo version number.
    Uses only the part from beginning up to specified length.
    Encodes a keyword "gh" and the length in a first part
    befor a dot.
    Second part is the actual hash or part of the hash.
    """
    prefix_decimal=str(str2int("gh"+str(length)))
    if not type(hashstr) is str or not len(hashstr) >= length:
        raise Exception("ERROR: hash is too short")
    hashstr=hashstr[:length]
    dec_hash=str(str2int(hashstr))
    return prefix_decimal+"."+dec_hash

def ver2gh(verstr,length):
    """
    Reverse gh2ver.
    Can only restore hex characters up until 
    length, the parameter value that
    was used during encoding.
    """
    prefix_need=str(str2int("gh"+str(length)))
    prefix_is,intstr=verstr.split(".")
    if prefix_need != prefix_is:
        raise Exception('ERROR: gh'+str(length)+'version numbers start with "'+prefix_decimal+'", .\n'
                        'The supplied one does not.')
    return int2str(int(intstr))

