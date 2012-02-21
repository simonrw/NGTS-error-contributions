#!/usr/bin/env python

'''
Calculate the distribution of fractions in the centre pixel for a psf of
given size as the psf is moved away from the centre pixel
'''

from numpy import *
from ppgplot import *
import argparse
from multiprocessing import Pool
from scipy.integrate import *
from Config import *

def Gaussian2D(y, x, fwhm, offset):
    sigma = fwhm / 2.35
    arg1 = (x-offset[0])**2
    arg2 = (y - offset[1])**2
    return exp(-(arg1 + arg2) / (2. * sigma**2))


def Ratio(fwhm=1.5, offset=(0., 0.)):
    '''
    Returns the ratio between the centre integral
    and full integral of the psf.
    '''
    return dblquad(Gaussian2D, -0.5, 0.5, lambda x: -0.5, lambda x: 0.5, args=(fwhm, offset))[0] / \
            dblquad(Gaussian2D, -Inf, Inf, lambda x: -Inf, lambda x: Inf, args=(fwhm, offset))[0] 

class App(object):
    """docstring for App"""
    def __init__(self, args):
        super(App, self).__init__()
        self.args = args
        self.fwhm = FWHM
        N = 50
        self.xvals = 10**linspace(-2, log10(3.*self.fwhm), N)

        pgopen(self.args.device)

        self.totalIntegral = dblquad(Gaussian2D, -Inf, Inf, lambda x: -Inf, lambda x: Inf, args=(self.fwhm, (0., 0.)))[0] 

        self.run()

    def __del__(self):
        pgclos()

    def run(self):
        pgenv(-0.1, 3., -6, 0, 0, 20)

        y1data = []
        y2data = []
        for x in self.xvals:
            y = 0.
            ratio = dblquad(Gaussian2D, -0.5, 0.5, lambda x: -0.5, lambda x: 0.5, args=(self.fwhm, (x, y)))[0] / \
                    self.totalIntegral
            y1data.append(log10(ratio))
            y = x
            ratio = dblquad(Gaussian2D, -0.5, 0.5, lambda x: -0.5, lambda x: 0.5, args=(self.fwhm, (x, y)))[0] / \
                    self.totalIntegral
            y2data.append(log10(Ratio(self.fwhm, (x, y))))

        pgsls(1)
        pgline(self.xvals, array(y1data))
        pgline(array([2.0, 2.1]), log10([0.3, 0.3]))
        pgsls(2)
        pgline(self.xvals, array(y2data))
        pgline(array([2.0, 2.1]), log10([0.15, 0.15]))
        pgsls(1)

        pgtext(2.2, log10(0.3), "Horizontal")
        pgtext(2.2, log10(0.15), "Diagonal")

        pglab("Distance / pix", "Fraction", "Central pixel flux for arbitrary offsets")

        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", help="PGPLOT device",
            required=False, type=str, default="1/xs")
    args = parser.parse_args()
    app = App(args)

