#!/usr/bin/env python

from ppgplot import *
import sys
import os.path
import argparse
import numpy as np
import cPickle
from jg.ctx import j20002gal
from subprocess import Popen, PIPE, call





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


        # list of field centres
        self.FieldCentre = [(60., -45.), (180., -45.), (300., -45.)]

        # set up exposure times to be equal in log space
        self.exptimes = 10**np.linspace(np.log10(5.), np.log10(3600.), 100)

        # NGTS instrument field of view
        '''
        Match the radius of search to the fov by equating areas

        \pi r^2 = x y
        r = sqrt(x * y / pi)
        '''
        npix = 2048
        pixscale = 4.97

        # get the dimensions in arcminutes
        x = npix * pixscale / 60.
        y = npix * pixscale / 60.
        self.radius = np.sqrt(x*y/np.pi)
        print "Searching within a radius of %f degrees, total area: %f sq degrees" % (
                self.radius / 60.,
                np.pi * (self.radius / 60.)**2,
                )

        # set up the exposure time array
        self.exptime = np.linspace(np.log10(5.), np.log10(3600.), 100)

        # load the fits
        fits = cPickle.load(open("fits.cpickle"))
        self.brightFit = fits['bright']
        self.darkFit = fits['dark']

        # saturation levels
        self.brightSaturLevel = self.brightFit(self.exptime)
        self.darkSaturLevel = self.darkFit(self.exptime)

        # plotting variables
        self.linestyles = [1, 2, 4]
        self.colours = [1, 2, 4]
        self.xmin = self.exptime.min()
        self.xmax = self.exptime.max()


        pgopen(self.args.device)

        # make a guess at the total number
        if self.args.fraction:
            self.ymin = 0.
            self.ymax = 1.1
            pgenv(self.xmin, self.xmax, self.ymin, self.ymax, 0, 10)
            self.yspacing = 0.05
        else:
            self.ymin = np.log10(10.)
            self.ymax = np.log10(70000)
            pgenv(self.xmin, self.xmax, self.ymin, self.ymax, 0, 30)
            self.yspacing = 0.15

        self.legend = (
                0.015 * (self.xmax - self.xmin) + self.xmin,
                0.95 * (self.ymax - self.ymin) + self.ymin,
                )
        self.linelength = 0.15






    def __del__(self):
        """
        Destructor
        """
        pgclos()


    def GetCatalogueData(self, ra, dec, band):
        # Check for the existence of finducac3
        if call("which finducac3", shell=True):
            # Can't find the binary on the users path
            binary = '/home/astro/phrfbf/build/bin/finducac3'

            # Going to try using SRW's binary
            if not os.path.isfile(binary):
                raise OSError("Cannot find binary 'finducac3' in "
                        "system path or SRW's path, contact him"
                        )
        else:
            # If call returns 0 then the binary is on the users
            # path
            binary = "finducac3"

        print binary


        cmd = [binary,
                str(ra), str(dec), '-r', str(self.radius),
                "-m", "1000000",
                ]

        pipe = Popen(" ".join(cmd), shell=True, stdout=PIPE, stderr=PIPE)
        result, error = pipe.communicate()

        imags = []
        for row in result.split("\n"):
            if "#" not in row:
                try:
                    # I band 
                    if band == "R":
                        imagval = float(row[221:227])
                    elif band == "I":
                        imagval = float(row[211:217])
                    else: raise ValueError("Invalid band passed")
                    # R band 
                except ValueError:
                    pass
                else:
                    imags.append(imagval)

        return np.array(imags)
        #parser = NOMADParser(ra, dec, self.radius)
        #results = parser.fetch()
        #rmags = []
        #for row in results:
            #rmagval = row['rmag']
            #if rmagval:
                #rmags.append(rmagval)
        #return np.array(rmags)


    def run(self):
        ii = 0
        for i, field in enumerate(self.FieldCentre):
            print "Analysing field %d,%d" % (field[0], field[1])
            galcoords = j20002gal(field[0], field[1])

            # Fetch the list of objects
            mags = self.GetCatalogueData(field[0], field[1], self.args.band)
            print "%d objects returned" % (mags.size,)

            # Get the number of saturated stars
            # Normalise to make fraction
            brightNumbers = np.array([mags[mags<level].size for level in self.brightSaturLevel])
            darkNumbers = np.array([mags[mags<level].size for level in self.darkSaturLevel])

            if self.args.fraction:
                brightNumbers = brightNumbers / float(mags.size)
                darkNumbers = darkNumbers / float(mags.size)
            else:
                brightNumbers = np.log10(brightNumbers)
                darkNumbers = np.log10(darkNumbers)

            # plot the bright line, dark line
            pgsci(self.colours[i])
            pgsls(2)
            pgline(self.exptime, brightNumbers)
            pgline(np.array([self.legend[0], self.legend[0] + self.linelength]), 
                    np.array([self.legend[1] - ii * self.yspacing, self.legend[1] - ii * self.yspacing]))
            pgsci(1)
            pgtext(np.array([self.legend[0] + self.linelength + 0.05,]),
                    np.array([self.legend[1] - ii * self.yspacing]),
                    "Bright (%.0f,%.0f -> %.1f,%.1f)" % (field[0], field[1], galcoords[0], galcoords[1]))
            pgsci(self.colours[i])

            ii += 1

            pgsls(4)
            pgline(self.exptime, darkNumbers)
            pgline(np.array([self.legend[0], self.legend[0] + self.linelength]), 
                    np.array([self.legend[1] - ii * self.yspacing, self.legend[1] - ii * self.yspacing]))
            pgsci(1)
            pgtext(np.array([self.legend[0] + self.linelength + 0.05,]),
                    np.array([self.legend[1] - ii * self.yspacing]),
                    "Dark")
            pgsci(self.colours[i])
            pgsls(1)
            pgsci(1)

            ii += 1

        if self.args.fraction:
            pglab("Exposure time / s", "Fraction of saturated stars", "%s band" % self.args.band)
        else:
            pglab("Exposure time / s", "Number of saturated stars", "%s band" % self.args.band)





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
                default="R", type=str, required=False)
        args = parser.parse_args()
        app = App(args)
        app.run()
