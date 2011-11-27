#!/usr/bin/env python

'''
Calculate the distribution of fractions in the centre pixel for a psf of
given size as the psf is moved away from the centre pixel
'''

import sys
from jg.subs import progressbarClass
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

        self.xRange = [-2.*self.fwhm, 2.*self.fwhm]
        self.yRange = [-2.*self.fwhm, 2.*self.fwhm]


        pgopen(self.args.device)
        self.run()

    def Integrate(self, lims, offset):
        return dblquad(Gaussian2D, lims[0], lims[1], lambda x: lims[2], lambda x: lims[3], args=(self.fwhm, offset))


    def __del__(self):
        pgclos()

    def run(self):
        total = self.Integrate((-np.Inf, np.Inf, -np.Inf, np.Inf), (0., 0.))[0]

        fractions = []
        pb = progressbarClass(self.N)
        counter = 0
        while counter < self.N:
            x = (self.xRange[1] - self.xRange[0]) * np.random.ranf() + self.xRange[0]
            y = (self.yRange[1] - self.yRange[0]) * np.random.ranf() + self.yRange[0]
            Fraction = self.Integrate((-0.5, 0.5, -0.5, 0.5), (x, y))[0] / total
            sys.stdout.flush()
            fractions.append(Fraction)
            pb.progress(counter+1)
            counter += 1

        fractions = np.log10(fractions)


        vals, edges = np.histogram(fractions, bins=50, range=(fractions.min(), 0), density=True)
        centres = edges[:-1] + np.diff(edges)[0] / 2.
        pgenv(fractions.min(), 0, 0, 1.1*vals.max(), 0, 10)

        pgbin(centres, vals, True)

        pglab("Fraction", "N", "Probability distribution")






if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", help="PGPLOT device",
            required=False, type=str, default="1/xs")
    parser.add_argument("-N", "--niter", help="Number of iterations",
            required=False, type=int, default=50)
    args = parser.parse_args()
    app = App(args)

