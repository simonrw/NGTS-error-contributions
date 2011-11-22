#!/usr/bin/env python

from ppgplot import *
from srw.NOMADParser import NOMADParser
import sys
import argparse
import numpy as np
import cPickle

class App(object):
    """
    Main application object
    """
    def __init__(self, args):
        """
        Constructor, sets up variables
        """
        super(App, self).__init__()


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

        # load the fits
        print cPickle.load(open("fits.cpickle"))

        pgopen("1/xs")



    def __del__(self):
        """
        Destructor
        """
        pgclos()

    def run(self):
        for field in self.FieldCentre[:1]:
            print "Analysing field %d,%d" % (field[0], field[1])

            # Fetch the list of objects
            parser = NOMADParser(field[0], field[1], self.radius)
            print "Fetching objects, please wait... ",
            sys.stdout.flush()
            Objects = parser.fetch()
            print "done. %d objects returned" % (len(Objects),)

            for exptime in self.exptimes:
                pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    app = App(args)
    app.run()
