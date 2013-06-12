#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Usage:
    PlotSaturationVsExposure.py [options] <file>

Options:
    -o, --output <output>       Output file name
    -h, --help                  Show this help
'''



import matplotlib.pyplot as plt
import numpy as np
import cPickle
from docopt import docopt

def main(args):
    with open(args['<file>']) as infile:
        data = cPickle.load(infile)

    bright_fit = data['bright']
    dark_fit = data['dark']

    xdata = np.linspace(np.log10(5), np.log10(50), 100)
    bright_ydata = bright_fit(xdata)
    dark_ydata = dark_fit(xdata)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(10 ** xdata, bright_ydata, 'r-', label='Bright')
    ax.plot(10 ** xdata, dark_ydata, 'g-', label='Dark')

    ax.set_xscale('log')

    ax.set_ylim(15, 8)
    # ax.set_ylim(*ax.get_ylim()[::-1])

    ticks = [1, 2, 5, 10, 20, 50]
    for method in ['set_xticks', 'set_xticklabels']:
        getattr(ax, method)(ticks)

    ax.set_xlim(3, 60)

    ax.set_xlabel(r'Exposure time / s')
    ax.set_ylabel(r'I magnitude saturation point')

    ax.legend(loc='best')
    ax.set_title(args['<file>'])
    plt.show()


if __name__ == '__main__':
    main(docopt(__doc__))
