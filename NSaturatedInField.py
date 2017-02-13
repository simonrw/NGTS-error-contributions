#!/usr/bin/env python

import sys
import os.path
import argparse
import numpy as np
import pickle
from jg.ctx import j20002gal
from subprocess import Popen, PIPE, call
from Config import *
import matplotlib.pyplot as plt
from NOMADFields import NOMADFieldsParser

class App(object):
    """
    Main application object
    """
    def __init__(self, args):
        """
        Constructor, sets up variables
        """
        super(App, self).__init__()
        self.args = args
        self.parser = NOMADFieldsParser()
        self.colours = ['r', 'k', 'b']


        # list of field centres
        self.FieldCentre = FieldCentre


        # NGTS instrument field of view
        '''
        Match the radius of search to the fov by equating areas

        \pi r^2 = x y
        r = sqrt(x * y / pi)
        '''
        npix = NAXIS1
        pixscale = PixScale

        # get the dimensions in arcminutes
        x = npix * pixscale / 60.
        y = npix * pixscale / 60.
        self.radius = np.sqrt(x*y/np.pi)
        print("Searching within a radius of %f degrees, total area: %f sq degrees" % (
                self.radius / 60.,
                np.pi * (self.radius / 60.)**2,
                ))

        # set up the exposure time array
        self.exptime = np.linspace(np.log10(5.), np.log10(3600.), 100)

        # load the fits
        fits = pickle.load(open("fits.cpickle"))
        self.brightFit = fits['bright']
        self.darkFit = fits['dark']

        # saturation levels
        self.brightSaturLevel = self.brightFit(self.exptime)
        self.darkSaturLevel = self.darkFit(self.exptime)

        # plotting variables
        self.xmin = self.exptime.min()
        self.xmax = self.exptime.max()




    def GetCatalogueData(self, field_id):
        table_name = 'field{:d}'.format(field_id)
        table = self.parser.getTable('/fields', table_name)
        vmags = table.cols.vmagnitude[:]
        return vmags[vmags > 0]

    def run(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for i, field in enumerate(self.FieldCentre):
            print("Analysing field %d,%d" % (field[0], field[1]))
            galcoords = j20002gal(field[0], field[1])

            # Fetch the list of objects
            mags = self.GetCatalogueData(i + 1)
            print("%d objects returned" % (mags.size,))

            # Get the number of saturated stars
            # Normalise to make fraction
            brightNumbers = np.array([mags[mags<level].size for level in self.brightSaturLevel])
            darkNumbers = np.array([mags[mags<level].size for level in self.darkSaturLevel])

            if self.args.fraction:
                brightNumbers = brightNumbers / float(mags.size)
                darkNumbers = darkNumbers / float(mags.size)


            ax.plot(10 ** self.exptime, brightNumbers, ls='--',
                    color=self.colours[i])
            ax.plot(10 ** self.exptime, darkNumbers, ls='-',
                    color=self.colours[i])

        ax.set_xscale('log')

        if self.args.fraction:
            ax.set_ylim(0, 1.1)

        ax.xaxis.set_major_formatter(plt.ScalarFormatter())
        ax.set_xlim(xmax=3400)
        ax.set_xlabel(r'Exposure time / s')

        if self.args.fraction:
            ax.set_ylabel(r'Saturated stars fraction')
        else:
            ax.set_ylabel(r'Saturated stars')


        plt.show()





if __name__ == '__main__':
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", r'.*use PyArray_AsCArray.*')
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--device", help="PGPLOT device",
                default='1/xs', required=False)
        parser.add_argument("-f", "--fraction", help="Plot as fraction",
                action="store_true", default=False)
        parser.add_argument("-b", "--band", help="Filter to use",
                default="I", type=str, required=False)
        args = parser.parse_args()
        app = App(args)
        app.run()
