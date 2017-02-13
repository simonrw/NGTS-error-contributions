#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Usage:
    PlotTheoryNoiseWithBinning.py <file>
'''

from docopt import docopt
import matplotlib.pyplot as plt
import numpy as np

import tables

def main(args):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    keys = ['read', 'sky', 'scintillation', 'source', 'total']
    colours = ['g', 'b', 'c', 'r', 'k']
    with tables.open_file(args['<file>']) as infile:
        group = infile.root.data

        print('Exposure time: {}s'.format(group._v_attrs.exptime))
        print('Integration time: {}s'.format(group._v_attrs.totaltime))

        mags = group.mag[:]


        for (key, colour) in zip(keys, colours):
            ax.plot(mags, getattr(group, key)[:], ls='-', color=colour)

        ax.axhline(1E-3, color='k', ls=':', zorder=-10)
        ax.axvline(group._v_attrs.crosspoint, color='k', ls=':', zorder=-10)
        ax.axvline(group._v_attrs.brightlimit, color='k', ls='-', zorder=-10)
        ax.axvline(group._v_attrs.darklimit, color='k', ls='--', zorder=-10)


    ax.set_yscale('log')
    ax.set_xlim(*ax.get_xlim()[::-1])
    ax.set_xlabel(r'I magnitude')
    ax.set_ylabel(r'Fractional error')
    plt.show()




if __name__ == '__main__':
    main(docopt(__doc__))
