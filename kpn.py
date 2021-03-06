from random import choice, random, randrange, shuffle
import sys

from distributions import b_model_time_series
from support import die, randrangexor

CMD_COMPUTATION = 0
CMD_READ = 1
CMD_WRITE = 2

class Node:
    def __init__(self, nodeid):
        self.nodeid = nodeid
        self.commands = []

    def compute(self, time):
        self.commands.append((CMD_COMPUTATION, time))       

    def is_empty(self):
        return len(self.commands) == 0

    def is_write(self, cmdi):
        return self.commands[cmdi][0] == CMD_WRITE

    def read(self, snodeid):
        self.commands.append((CMD_READ, snodeid))

    def set_write(self, cmdi, wsize):
        (cmd, par) = self.commands[cmdi]
        assert(cmd == CMD_WRITE)
        (dnodeid, dontcare) = par
        self.commands[cmdi] = (cmd, (dnodeid, wsize))

    def write(self, dnodeid, wsize = None):
        self.commands.append((CMD_WRITE, (dnodeid, wsize)))

    def __str__(self):
        l = ['node', str(self.nodeid), str(len(self.commands))]
        for (cmd, par) in self.commands:
            if cmd == CMD_COMPUTATION:
                l += ['c', str(par)]
            elif cmd == CMD_READ:
                l += ['r', str(par)]
            else:
                l += ['w', str(par[0]), str(par[1])]
        return ' '.join(l)

def power_of_two(x):
    i = 1
    while i < x:
        i *= 2
    return i

def round_to_integer_values(values):
    return map(lambda x: max(1, int(round(x))), values)

def gen_write_values(nodes, options):
    wevents = []
    for node in nodes:
        i = 0
        while i < len(node.commands):
            if node.is_write(i):
                wevents.append((node.nodeid, i))
            i += 1
    shuffle(wevents)

    # b model can only generate power of two sized series, so we generate
    # extra if necessary, and cut down to the original size, and then
    # normalize the sum of time series values into options.wsize.
    # And finally round to integer values.

    # 1. Generate at least as large power of two series
    wsizes = b_model_time_series(options.wb, 1.0, power_of_two(len(wevents)))

    # 2. cut down extra
    wsizes = wsizes[0 : len(wevents)]

    # 3. Normalize time series values into sum of options.wsize
    s = sum(wsizes)
    wsizes = map(lambda x: x * options.wsize / s, wsizes)

    # 4. Round to integer values
    wsizes = round_to_integer_values(wsizes)

    sys.stderr.write('Sum of communication bytes: %d (%d events)\n' %(sum(wsizes), len(wsizes)))

    i = 0
    for (nodeid, cmdi) in wevents:
        nodes[nodeid].set_write(cmdi, wsizes[i])
        i += 1

def ancestor(d, s, links):
    """ DFS starting from node d, terminates when node s is encountered or
    all reachable nodes from d have been visited. Returns True iff node s
    is encountered, that is, d is an ancestor of s. """

    visited = set()
    lifo = [d]
    while len(lifo) > 0:
        node = lifo.pop()
        if node in visited:
            continue
        visited.add(node)
        if node == s:
            return True
        for child in links[node].keys():
            lifo.append(child)

    return False

def acyclic_destination(s, nnodes, links):
    dests = range(nnodes)
    shuffle(dests)
    for d in dests:
        if d == s:
            continue
        if not ancestor(d, s, links):
            return d
    return None

def gen_targets(n, options):
    targets = {}
    mvec = []
    for rnodeid in xrange(n):
        l = []
        for dnodeid in xrange(n):
            if dnodeid == rnodeid:
                continue
            l.append(dnodeid)
        if options.tdist != None:
            shuffle(l)
            m = 1 + randrange(int(round(n * options.tdist)))
            l = l[0 : m]
        mvec.append(len(l))
        targets[rnodeid] = l
    sys.stderr.write('Average number of targets: %f\n' %(float(sum(mvec)) / len(mvec)))
    return targets

def generate_kpn(options):
    if options.cevents <= 0:
        die('Invalid number of computation events: %d\n' %(options.cevents))
    if power_of_two(options.cevents) != options.cevents:
        die('Not a power of two number of computation events: %d\n' %(options.cevents))

    if options.nnodes < 2:
        die('Invalid number of nodes: %d\n' %(options.nnodes))
    if options.wprob < 0 or options.wprob >= 1:
        die('Invalid write probablity: %f\n' %(options.wprob))
    if options.wsize < 0:
        die('Invalid write size: %d\n' %(options.wsize))
    if options.ctime <= 0:
        die('Invalid write size: %d\n' %(options.ctime))
    if options.cb < 0 or options.cb > 1:
        die('Invalid computation b value: %f\n' %(options.cb))
    if options.wb < 0 or options.wb > 1:
        die('Invalid communication b value: %f\n' %(options.wb))
    if options.tdist != None and (options.tdist <= 0 or options.tdist > 1.0):
        die('Invalid target distribution value: %f\n' %(options.tdist))

    nodes = map(lambda i: Node(i), range(options.nnodes))

    sys.stderr.write('%d nodes\n' %(options.nnodes))

    ctimes = b_model_time_series(options.cb, options.ctime, options.cevents)
    ctimes = round_to_integer_values(ctimes)
    sys.stderr.write('Sum of computation times: %d (%d events)\n' %(sum(ctimes), len(ctimes)))

    links = []
    for nodeid in xrange(len(nodes)):
        links.append({})

    targets = gen_targets(len(nodes), options)

    cevents = 0
    wevents = 0
    firstnode = True
    writelocked = False
    while cevents < options.cevents:
        if firstnode:
            rnodeid = 0
        else:
            rnodeid = randrange(0, len(nodes))

        rnode = nodes[rnodeid]

        if writelocked or random() < options.wprob:
            writelocked = True
            if options.acyclic:
                dnodeid = acyclic_destination(rnodeid, len(nodes), links)
            else:
                dnodeid = choice(targets[rnodeid])
            if dnodeid == None:
                continue
            writelocked = False
            dnode = nodes[dnodeid]
            dnode.read(rnodeid)
            rnode.write(dnodeid)
            wevents += 1
            links[rnodeid][dnodeid] = None
        else:
            rnode.compute(ctimes[cevents])
            cevents += 1

        firstnode = False

    if wevents > 0:
        gen_write_values(nodes, options)

    ncommands = 0
    for node in nodes:
        ncommands += len(node.commands)
        if node.is_empty():
            sys.stderr.write('Node %d is empty\n' %(node.nodeid))
    sys.stderr.write('%d commands\n' %(ncommands))

    if options.dot != None:
        write_dot(options.dot, len(nodes), links)

    for node in nodes:
        print node

def write_dot(fname, n, links):
    try:
        f = open(fname, 'w')
    except IOError:
        die('Can not open %s for writing\n' %(fname))

    f.write('digraph kpn {\n')
    for nodeid in xrange(n):
        f.write('\tnode%d [];\n' %(nodeid))
    for nodeid in xrange(n):
        for d in links[nodeid].keys():
            f.write('\tnode%d -> node%d;\n' %(nodeid, d))
    f.write('}\n')
    f.close()
