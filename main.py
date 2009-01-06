#!/usr/bin/env python

from optparse import OptionParser

from kpn import generate_kpn

def main():
    parser = OptionParser(version = 'kpn-generator 0.01')
    parser.add_option('-c', '--computation-events',
                      dest = 'cevents',
                      type = 'int',
                      default = 32,
                      metavar = 'C',
                      help = 'set number of computation events C. C must be a power of two. The default is 32.')
    parser.add_option('-n', '--nodes',
                      dest = 'nnodes',
                      type = 'int', 
                      default = 10,
                      metavar = 'N',
                      help = 'set number of nodes N. The default is 10.')
    parser.add_option('-p', '--write-probability',
                      dest = 'wprob',
                      type = 'float',
                      default = 0.5,
                      metavar = 'P',
                      help = 'set write probability P. The default is 0.5.')
    parser.add_option('-s', '--write-size',
                      dest = 'wsize',
                      type = 'int',
                      default = 1024,
                      metavar = 'S',
                      help = 'set total write size S. The default is 1024.')
    parser.add_option('-t', '--time',
                      dest = 'ctime',
                      type = 'int',
                      default = 1024,
                      metavar = 'T',
                      help = 'set total computation time T. The default is 1024.')
    parser.add_option('-x', '--comp-b',
                      dest = 'cb',
                      type = 'float',
                      default = 0.7,
                      metavar = 'b',
                      help = 'set b model value in range [0, 1] for computation time randomization. The default is 0.7.')
    parser.add_option('-y', '--comm-b',
                      dest = 'wb',
                      type = 'float',
                      default = 0.7,
                      metavar = 'b',
                      help = 'set b model value in range [0, 1] for communication size randomization. The default is 0.7.')
    (options, args) = parser.parse_args()

    generate_kpn(options)

if __name__ == '__main__':
    main()
