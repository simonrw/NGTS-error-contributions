#!/usr/bin/env python

import sys
import os
import os.path
from srw import pghelpers as pgh
import argparse
#from subprocess import Popen, call, PIPE, STDOUT
#import matplotlib.pyplot as plt
import numpy as np
import srw
#import pyfits
import ppgplot as pg
import AstErrors as ae
import cPickle
from Config import *


class App(object):
    '''
    Main application object for the project
    '''
    source = []
    sky = []
    read = []
    scin = []
    total = []
    def __init__(self, args):
        '''
        Constructor
        '''
        super(App, self).__init__()
        self.args = args
        self.exptime = self.args.exptime

        self.fileDir = os.path.dirname(__file__)

        self.mag = np.linspace(7, 18., 1000)

        self.plotLimits = (self.mag.max(), self.mag.min(),
                -6, -1)

        self.run()

    def plotWASPData(self):
        '''
        Overlays the wasp data from Joao
        '''
        waspdata = cPickle.load(open(
            os.path.join(self.fileDir,
            "JoaoData", "data.cpickle")
            ))

        # Convert I to V
        imagCorrection = 0.27
        with pgh.change_colour(15):
            pg.pgpt(waspdata['vmag'] + imagCorrection,
                    np.log10(waspdata['binned']), 1)

    def plotNGTSData(self):
        '''
        Overlays the NGTS data
        '''
        ngtsdata = cPickle.load(open(
            os.path.join(self.fileDir,
                "NGTSData", "NGTSData.cpickle")
            ))

        with pgh.change_colour(15):
            pg.pgpt(ngtsdata['mag'], np.log10(ngtsdata['sd']), 1)

    def saturationLimit(self):
        fits = cPickle.load(
                open(os.path.join(self.fileDir,
                    "fits.cpickle"))
                )
        self.brightLimit = fits['bright'](np.log10(self.exptime))
        self.darkLimit = fits['dark'](np.log10(self.exptime))

        # Get the plot limits
        with pgh.change_colour(15):
            with pgh.change_linestyle(4):
                pg.pgline(np.array([self.brightLimit, self.brightLimit]),
                        np.array([self.plotLimits[2], self.plotLimits[3]]))
            pg.pgline(np.array([self.darkLimit, self.darkLimit]),
                    np.array([self.plotLimits[2], self.plotLimits[3]]))



    def run(self):
        '''
        Main function
        '''
        radius = 1.5  # Radius of flux extraction aperture
        npix = np.pi * radius ** 2
        detector = ae.NGTSDetector()
        extinction = 0.06
        targettime = self.args.totaltime
        height = 2400.
        apsize = 0.2
        airmass = 1.
        readnoise = ReadNoise
        zp = srw.ZP(1.)

        if self.args.skylevel == "dark": skypersecperpix = 50.
        elif self.args.skylevel == "bright": skypersecperpix = 160.
        else: raise RuntimeError("Invalid sky type entered")


        for mag in self.mag:
            errob = ae.ErrorContribution(mag, npix, detector.readTime(),
                    extinction, targettime, height, apsize, zp, readnoise)
            self.source.append(errob.sourceError(airmass, self.exptime))
            self.sky.append(errob.skyError(airmass, self.exptime,
                skypersecperpix))
            self.read.append(errob.readError(airmass, self.exptime))
            self.scin.append(errob.scintillationError(airmass, self.exptime))
            self.total.append(errob.totalError(airmass, self.exptime,
                skypersecperpix))

        self.source = np.log10(self.source)
        self.sky = np.log10(self.sky)
        self.read = np.log10(self.read)
        self.scin = np.log10(self.scin)
        self.total = np.log10(self.total)

        with pgh.open_plot(self.args.device):
            pg.pgenv(self.plotLimits[0], self.plotLimits[1],
                    self.plotLimits[2], self.plotLimits[3],
                    0, 20)

            if self.args.plotwasp: self.plotWASPData()
            if self.args.plotngts: self.plotNGTSData()

            if self.args.satlimit: self.saturationLimit()

            # Draw the 1mmag line
            with pgh.change_linestyle(2), pgh.change_colour(15):
                pg.pgline(np.array([self.mag.max(), self.mag.min()]),
                        np.array([-3., -3.]))

            # Plot a line at the point when the total error meets
            # the 1mmag line
            distFrom1mmag = np.abs(self.total + 3.)
            ind = distFrom1mmag==distFrom1mmag.min()
            self.crossPoint = self.mag[ind][0]


            with pgh.change_colour(15), pgh.change_linestyle(2):
                pg.pgline(np.array([self.crossPoint, self.crossPoint]),
                        np.array([-6, -1])
                        )

            # Plot the theory lines
            for colour, ydata in zip(
                    [2, 4, 3, 5, 1],
                    [self.source, self.sky, self.read, self.scin, self.total]):
                with pgh.change_colour(colour):
                    pg.pgline(self.mag, ydata)


            pg.pglab(r"I magnitude", "Fractional error", r"t\de\u: %.1f s, "
                    "t\dI\u: %.1f hours, "
                    "1mmag @ %.3f mag" % (self.exptime, targettime/3600.,
                        self.crossPoint))

        if self.args.verbose:
            if self.darkLimit:
                print "SATLEVEL DARK: %f" % self.darkLimit

            if self.brightLimit:
                print "SATLEVEL BRIGHT: %f" % self.brightLimit

            print "CROSSPOINT: %f" % self.crossPoint









if __name__ == '__main__':
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", r'.*use PyArray_AsCArray.*')
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument("-t", "--totaltime", help="Total integration time",
                    default=3600., type=float, required=False)
            parser.add_argument("-e", "--exptime", help="Science exposure time",
                    type=float, required=True)
            parser.add_argument("-s", "--skylevel", help="Sky type (bright "
                                "or dark", choices=["bright", "dark"],
                                type=lambda val: val.lower(),
                                required=False, default="dark")
            parser.add_argument("-d", "--device", help="PGPLOT device",
                    required=False, default="/xs")
            parser.add_argument("-w", "--plotwasp", help="Overlay some WASP staring data",
                    action="store_true", default=False)
            parser.add_argument("-n", "--plotngts", help="Overlay some NGTS prototype data",
                    action="store_true", default=False)
            parser.add_argument("-S", "--satlimit", help="Do not plot saturation limit",
                    action="store_false", default=True)
            parser.add_argument("-v", "--verbose", default=False, help="Print extra information",
                    action="store_true")
            args = parser.parse_args()
            app = App(args)
        except KeyboardInterrupt:
            print >> sys.stderr, "Interrupt caught, exiting..."
            sys.exit(0)
