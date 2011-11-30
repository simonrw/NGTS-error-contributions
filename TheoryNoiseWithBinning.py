#!/usr/bin/env python

import sys
#import os
#import os.path
import argparse
#from subprocess import Popen, call, PIPE, STDOUT
#import matplotlib.pyplot as plt
import numpy as np
import srw
#import pyfits
from ppgplot import *
import NGTSErrors as nge


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

        self.mag = np.linspace(7, 18., 1000)

        self.run()

    def run(self):
        '''
        Main function
        '''
        npix = 1.5**4 * np.pi
        exptime = self.args.exptime
        readtime = 2048. * (38E-6 + 2048. / 3E6)
        extinction = 0.06
        targettime = self.args.totaltime
        height = 2400.
        apsize = 0.2
        airmass = 1.
        readnoise = 11.7
        zp = srw.ZP(1.)

        if self.args.skylevel == "dark": skypersecperpix = 50.
        elif self.args.skylevel == "bright": skypersecperpix = 160. 
        else: raise RuntimeError("Invalid sky type entered")


        for mag in self.mag:
            errob = nge.ErrorContribution(mag, npix, exptime, readtime,
                    extinction, targettime, height, apsize, zp)
            self.source.append(errob.sourceError(airmass))
            self.sky.append(errob.skyError(airmass, skypersecperpix))
            self.read.append(errob.readError(airmass, readnoise))
            self.scin.append(errob.scintillationError(airmass)) 
            self.total.append(errob.totalError(airmass, readnoise, skypersecperpix))

        self.source = np.log10(self.source)
        self.sky = np.log10(self.sky)
        self.read = np.log10(self.read)
        self.scin = np.log10(self.scin)
        self.total = np.log10(self.total)

        pgopen("2/xs")
        pgenv(self.mag.max(), self.mag.min(), -6, -1, 0, 20)

        # Draw the 1mmag line
        pgsls(2)
        pgsci(15)
        pgline(np.array([self.mag.max(), self.mag.min()]),
                np.array([-3., -3.]))
        pgsci(1)
        pgsls(1)

        pgsci(2)
        ylevel = -5.8
        pgline(self.mag, self.source)
        pgline(np.array([17., 17.5]),
                np.array([ylevel, ylevel])
                )
        pgsci(1)
        pgtext(16.7, ylevel, r"Source")

        pgsci(3)
        ylevel += 0.2
        pgline(self.mag, self.sky)
        pgline(np.array([17., 17.5]),
                np.array([ylevel, ylevel])
                )
        pgsci(1)
        pgtext(16.7, ylevel, r"Sky")

        pgsci(4)
        ylevel += 0.2
        pgline(self.mag, self.read)
        pgline(np.array([17., 17.5]),
                np.array([ylevel, ylevel])
                )
        pgsci(1)
        pgtext(16.7, ylevel, r"Read")

        pgsci(5)
        ylevel += 0.2
        pgline(self.mag, self.scin)
        pgline(np.array([17., 17.5]),
                np.array([ylevel, ylevel])
                )
        pgsci(1)
        pgtext(16.7, ylevel, r"Scintillation")

        pgsci(1)
        ylevel += 0.2
        pgline(self.mag, self.total)
        pgline(np.array([17., 17.5]),
                np.array([ylevel, ylevel])
                )
        pgsci(1)
        pgtext(16.7, ylevel, r"Total")
        pgsci(1)

        # Plot a line at the point when the total error meets
        # the 1mmag line
        distFrom1mmag = np.abs(self.total + 3.)
        ind = distFrom1mmag==distFrom1mmag.min()
        crossPoint = self.mag[ind][0]


        pgsls(2)
        pgsci(15)
        pgline(np.array([crossPoint, crossPoint]),
                np.array([-6, -1])
                )
        pgsci(1)
        pgsls(1)



        pglab(r"I magnitude", "Fractional error", r"t\de\u: %.1f s, "
                "t\dI\u: %.1f hours, sky: %s, 1mmag @ %.3f mag" % (exptime, targettime/3600.,
                    self.args.skylevel, crossPoint))
        pgclos()





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
            args = parser.parse_args()
            app = App(args)
        except KeyboardInterrupt:
            print >> sys.stderr, "Interrupt caught, exiting..."
            sys.exit(0)
