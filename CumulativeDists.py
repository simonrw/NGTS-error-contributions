#!/usr/bin/env python
# encoding: utf-8

'''
Given the high precision range, plot the number of stars for a given magnitude
to assess which exposure time gives the maximum number of bright objects
'''

from srw import pghelpers as pgh
import numpy as np
import ppgplot as pg
from BesanconParser import BesanconParser
from srw import cumulative_hist
import argparse
import cPickle
import os
from scipy.interpolate import interp1d
import contextlib


@contextlib.contextmanager
def open_bparser():
    bp = BesanconParser()
    yield bp
    bp.close()


def main(args):
    with open(os.path.join(os.path.dirname(__file__),
        'precisiondata.cpickle')) as filedata:
        exptimes, crosspoints, satpoints = cPickle.load(filedata)

    x_range = [8, 16]

    interpcross = interp1d(exptimes, crosspoints, kind='linear')
    interpsat = interp1d(exptimes, satpoints, kind='linear')

    selection_cut = '((typ == 4) | (typ == 5) | (typ == 6)) & (cl == 5)'

    linestyles = [2, 3, 4]
    exptimes = [10, 20, 30]

    with open_bparser() as bp, pgh.open_plot('1/xs'):

        pg.pgvstd()
        pg.pgswin(x_range[0], x_range[1], 0, 1.1)

        nodes = [bp.getTable('/fields', 'field{:d}'.format(i))
                for i in xrange(1, 4)]

        all_vmags = []
        for node in nodes:
            all_vmags.extend(np.array([sum([row['imagnitude'], row['vmi']])
                for row in node.where(selection_cut)]))

        all_vmags = np.array(all_vmags)

        for exptime, ls in zip(exptimes, linestyles):
            satpoint = interpsat(exptime)
            crosspoint = interpcross(exptime)

            selected = all_vmags[(all_vmags > satpoint) & (all_vmags <
                crosspoint)]

            xdata, ydata = cumulative_hist(np.array(selected),
                    min_val=x_range[0], max_val=x_range[1])

        with pgh.change_linestyle(ls):
            pg.pgbin(xdata, ydata, False)


        pg.pgbox('bcnst', 0, 0, 'bcnst', 0, 0)
        pg.pglab(r'V magnitude', 'High precision fraction', '')

        # Create the legend
        pg.pgsvp(0.7, 0.9, 0.1, 0.3)
        pg.pgswin(0., 1., 0., 1.)

        for i, (exptime, ls) in enumerate(zip(exptimes, linestyles)):
            yval = 0.1 + 0.8 * i / len(exptimes)

            with pgh.change_linestyle(ls):
                pg.pgline(np.array([0.2, 0.4]), np.ones(2) * yval)

            pg.pgtext(0.5, yval, r'{:d} s'.format(exptime))

        #pg.pgbox('bcnst', 0, 0, 'bcnst', 0, 0)




if __name__ == '__main__':
    parser = argparse.ArgumentParser()


    main(parser.parse_args())
