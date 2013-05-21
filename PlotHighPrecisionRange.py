#!/usr/bin/env python
# encoding: utf-8


'''
This script plots the data generated
by HighPrecisionRange.py
'''

import cPickle
import os.path
import tables
import argparse
import matplotlib.pyplot as plt


def main(args):
    """Main program
    @return: @todo
    """

    filename = os.path.join(
            os.path.dirname(__file__),
            "precisiondata.cpickle"
            )

    exptimes, crosspoints, darkpoints, brightpoints = cPickle.load(open(filename, 'rb'))

    ind = exptimes >= 5
    exptimes, crosspoints, darkpoints, brightpoints = [data[ind]
            for data in [exptimes, crosspoints, darkpoints, brightpoints]]

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.plot(exptimes, crosspoints, 'k--')
    ax.plot(exptimes, darkpoints, 'k--')

    ax.fill_between(exptimes, crosspoints, darkpoints,
            color='0.9')
    ax.plot(exptimes, brightpoints, 'k:')

    # Invert the y axis
    ax.set_ylim(ax.get_ylim()[1], ax.get_ylim()[0])

    ax.set_xlabel("Exposure time / s")
    ax.set_ylabel("I magnitude")
    ax.set_title("High precision (>1mmag precision, not saturating)")
    ax.set_xscale('log')
    ax.xaxis.set_major_formatter(plt.ScalarFormatter())

    ticks = [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100]
    ax.set_xticks(ticks)
    ax.set_xticklabels(ticks)
    ax.set_xlim(0.9 * exptimes.min(), 1.1 * exptimes.max())

    with tables.openFile('highprecisionrange.h5', 'w') as outfile:
        outfile.createArray('/', 'exptimes', exptimes)
        outfile.createArray('/', 'crosspoints', crosspoints)
        outfile.createArray('/', 'darklimits', darkpoints)
        outfile.createArray('/', 'brightlimits', brightpoints)


    if args.output:
        plt.savefig(args.output)
    else:
        plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="Output device",
            type=str, required=False, default=None)
    args = parser.parse_args()
    main(args)
