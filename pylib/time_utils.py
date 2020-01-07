from time import localtime,time

def get_useful_localtime_string(decimal_sec_digits=2,dec_sec_sep="."):
    """
    Returns 12 chars long, easy to read and comparable time string.
    Format reading: century , day of year, second of day
    Example: "20___7_52001"
    This is the compromise of unix time and a full
    time string like "Tue 07 Jan 2020 02:15:14 PM CET",
    which is 31 characters long.
    It is fixed lenght , zeros are padded with underscores.
    """
    t=localtime()
    century     = t.tm_year%100
    day_of_year = t.tm_yday
    sec_of_day  = t.tm_hour*3600+t.tm_min*60+t.tm_sec
    if decimal_sec_digits > 0:
        dec_sec = int(round(time() % 1,decimal_sec_digits)*10**decimal_sec_digits)
        dec_sec_str = (dec_sec_sep+"{:0>"+str(decimal_sec_digits)+"d}").format(dec_sec)
    else:
        dec_sec_str = ""
    # format string, pad the fields left side with "_"
    return "{:_>2d}_{:_>3d}_{:_>5d}".format(century,day_of_year,sec_of_day) + dec_sec_str
