from math import floor

def shorten_msg(msg,max_len):
    """
    shortens the message, place inside newlines
    """
    if len(msg) > max_len:
        h0=floor(max_len/2)
        h1=max_len-h0
        msg=msg[:h0]+"\n   ---skipped---   \n" + msg[ - h1:]
    return msg
