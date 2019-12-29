
def get_default_args(argument_parser):
    """
    returns a list with option_strings,default
    from a argparse.ArgumentParser
    """
    lines=[]
    for a in argument_parser._actions:
        lines.append([a.option_strings,a.default])
    return lines
