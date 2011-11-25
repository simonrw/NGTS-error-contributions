#!/usr/bin/env python

'''
Calculate the distribution of fractions in the centre pixel for a psf of
given size as the psf is moved away from the centre pixel
'''

import argparse
from scipy.integrate import dblquad
import numpy as np
from ppgplot import *

def Gaussian2D(y, x, fwhm, offset):
    sigma = fwhm / 2.35
    arg1 = (x-offset[0])**2
    arg2 = (y - offset[1])**2
    return np.exp(-(arg1 + arg2) / (2. * sigma**2))



class App(object):
    """docstring for App"""
    def __init__(self, args):
        super(App, self).__init__()
        self.args = args
        self.fwhm = 1.5
        self.N = self.args.niter

        xRange = [-2.*self.fwhm, 2.*self.fwhm]
        yRange = [-2.*self.fwhm, 2.*self.fwhm]

        self.xvals = (xRange[1] - xRange[0]) * np.random.random(self.N) + xRange[0]
        self.yvals = (yRange[1] - yRange[0]) * np.random.random(self.N) + yRange[0]

        pgopen(self.args.device)
        self.run()

    def Integrate(self, lims, offset):
        return dblquad(Gaussian2D, lims[0], lims[1], lambda x: lims[2], lambda x: lims[3], args=(self.fwhm, offset))


    def __del__(self):
        pgclos()

    def run(self):
        total = self.Integrate((-np.Inf, np.Inf, -np.Inf, np.Inf), (0., 0.))[0]

        fractions = []
        for y in self.yvals:
            for x in self.xvals:
                Fraction = self.Integrate((-0.5, 0.5, -0.5, 0.5), (x, y))[0] / total
                print "%.1f %.1f => %.3f" % (x, y, Fraction)
                fractions.append(Fraction)

        fractions = np.log10(fractions)


        vals, edges = np.histogram(fractions, bins=50, range=(-4, 0))
        centres = edges[:-1] + np.diff(edges)[0] / 2.
        pgenv(-4, 0, 0, 1.1*vals.max(), 0, 10)

        pgsci(15)
        pgerrb(6, centres, vals, np.sqrt(vals), 1.0)
        pgsci(1)
        pgbin(centres, vals, True)






if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", help="PGPLOT device",
            required=False, type=str, default="1/xs")
    parser.add_argument("-N", "--niter", help="Number of iterations",
            required=False, type=int, default=100)
    args = parser.parse_args()
    app = App(args)

