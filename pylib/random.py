from fractions import Fraction
from random import choice


def random_bool(probability):
    """
    get a random choice with desired probability.
    Uses the python random choice function to
    pick a bool out of a list.
    To avoid to much memory usage because of
    a long list, it is best to pass in a "Fraction"
    from the fractions module.
    The denominator is equal to the list length.
    The used list length is choosen to provide
    the required resolution to match the probabilty
    the best.
    The exactness relies on the exactness of
    the fraction that is made by the Fraction
    class from the fractions module.
    Also relies the exactness
    on the randomness of the choices function,
    of the random module, that is unknown to me.
    """
    fraction = Fraction(probability)
    length_true  = fraction.numerator
    length_false = fraction.denominator - fraction.numerator
    lt = [True]  * length_true
    lf = [False] * length_false
    l = lt+lf
    return choice(l)

def random_bool_of_num(numTrue,numThings):
    """
    Returns a random choice from a pool of booleans
    that has "numTrue" things that are true in it,
    the other ones are false,
    and that has a pool size of "numThings" in total.
    """
    probability  = Fraction( numTrue , numThings )
    return random_bool(probability)
