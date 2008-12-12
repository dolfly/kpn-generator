from random import choice
import sys

def b_model_time_series(b, N, T):
    """ b-model time series generation. Divide mass N into T pieces.
    At each iteration, it splits one piece into two pieces so that the
    other half gets proportion b of the original mass, and the other
    half gets the rest: 1 - b.

    Inputs:

    b - division proportion in range (0, 1)
    N - total mass to divide (any non-negative number)
    T - number of pieces to divide mass into (any power of two integer)

    Special cases:

    If b == 0 or b == 1, all mass is put into a single piece.
    If b == 0.5, all mass is divided equally among pieces.
    """

    # Input checking
    b = float(b)
    assert(b >= 0 and b <= 1)
    assert(type(T) == int)
    assert(T > 0)

    # Verify that T is a power of two
    x = 1
    while x < T:
        x *= 2
    assert(x == T)

    # Functionality
    I = [float(N)]
    while T > 1:
        i = 0
        while i < len(I):
            Iv = I.pop(i)
            c = choice([b, 1 - b])
            I.insert(i, c * Iv)
            I.insert(i, (1 - c) * Iv)
            i += 2
        T /= 2

    return I

def bmodeltest():
    b = 0.7
    N = 16
    T = 32
    I = b_model_time_series(b, N, T)
    for v in I:
        sys.stdout.write('%.3f ' %(v))
    sys.stdout.write('\n')

if __name__ == '__main__':
    bmodeltest()
