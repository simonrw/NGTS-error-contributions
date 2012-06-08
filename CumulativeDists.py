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
from NOMADFields import NOMADFieldsParser
import contextlib


@contextlib.contextmanager
def open_bparser():
    bp = BesanconParser()
    yield bp
    bp.close()


@contextlib.contextmanager
def open_nparser():
    np = NOMADFieldsParser()
    yield np
    np.close()


def get_nomad_mag_data():
    with open_nparser() as nparse:
        nodes = [nparse.getTable('/fields', 'field{:d}'.format(i))
                for i in xrange(1, 4)]
        all_vmags = []
        for node in nodes:
            all_vmags.extend([row['vmagnitude'] for row in
                node.where('(vmagnitude > 7) & (vmagnitude < 15)')])

    all_vmags = np.array(all_vmags)

    return all_vmags



def get_besancon_mag_data():
    with open_bparser() as bp:
        selection_cut = '''((typ == 4) | (typ == 5) | (typ == 6) | (typ == 7)) & (cl == 5) & (imagnitude + vmi < 15) & (imagnitude + vmi > 7)'''
        #selection_cut = 'cl != 0'
        nodes = [bp.getTable('/fields', 'field{:d}'.format(i))
                for i in xrange(1, 4)]

        all_vmags = []
        for node in nodes:
            all_vmags.extend([sum([row['imagnitude'], row['vmi']])
                for row in node.where(selection_cut)])

        all_vmags = np.array(all_vmags)

    return all_vmags



def main(args):
    with open(os.path.join(os.path.dirname(__file__),
        'precisiondata.cpickle')) as filedata:
        exptimes, crosspoints, satpoints = cPickle.load(filedata)

    x_range = [9, 14]

    interpcross = interp1d(exptimes, crosspoints, kind='linear')
    interpsat = interp1d(exptimes, satpoints, kind='linear')


    N = 5
    colours = np.arange(2, 2 + N, 1)
    exptimes = np.arange(1, N + 1) * 10
    if args.besancon:
        all_vmags = get_besancon_mag_data()
        yhigh = 0.3
    else:
        all_vmags = get_nomad_mag_data()
        yhigh = 0.4

    ytot = yhigh * len(all_vmags)


    with pgh.open_plot(args.output):

        pg.pgvstd()


        pg.pgswin(x_range[0], x_range[1], 0, yhigh)
        for exptime, colour in zip(exptimes, colours):
            satpoint = interpsat(exptime)
            crosspoint = interpcross(exptime)

            selected = all_vmags[(all_vmags > satpoint) & (all_vmags <=
                crosspoint)]
            print exptime, len(selected)


            xdata, ydata = cumulative_hist(np.array(selected),
                    min_val=x_range[0], max_val=x_range[1], norm=len(all_vmags))

            with pgh.change_colour(colour):
                pg.pgbin(xdata, ydata, False)


        pg.pgbox('bcnst', 0, 0, 'bcnst', 0, 0)
        pg.pglab(r'V magnitude', 'High precision fraction', '')
        # Label the right hand side
        pg.pgswin(x_range[0], x_range[1], 0, ytot)
        pg.pgbox('', 0, 0, 'smt', 0, 0)
        pg.pgmtxt('r', 2., 0.5, 0.5, 'N')

        # Create the legend
        pg.pgsvp(0.7, 0.9, 0.1, 0.3)
        pg.pgswin(0., 1., 0., 1.)

        for i, (exptime, colour) in enumerate(zip(exptimes, colours)):
            yval = 0.1 + 0.8 * i / len(exptimes)

            with pgh.change_colour(colour):
                pg.pgline(np.array([0.2, 0.4]), np.ones(2) * yval)

            pg.pgtext(0.5, yval, r'{:d} s'.format(exptime))

        #pg.pgbox('bcnst', 0, 0, 'bcnst', 0, 0)




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', type=str, default='1/xs',
            help="Output device")
    parser.add_argument('-b', '--besancon', action='store_true',
            default=False, help="Use Besancon model data")


    main(parser.parse_args())
