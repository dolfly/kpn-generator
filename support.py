import random
import sys

def die(msg):
    sys.stderr.write('%s' %(msg))
    sys.exit(1)

def randrangexor(a, b, n):
    if n < a or n >= b:
        # n is not in range [a, b) so no conflict can happen
        return random.randrange(a, b)

    x = random.randrange(a, b - 1)
    if x >= n:
        x += 1

    return x
