#!/usr/bin/env python

'''
Calculate the distribution of fractions in the centre pixel for a psf of
given size as the psf is moved away from the centre pixel
'''

import argparse
from scipy.integrate import dblquad
import numpy as np

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

    def Integrate(self, lims, offset):
        return dblquad(Gaussian2D, lims[0], lims[1], lambda x: lims[2], lambda x: lims[3], args=(self.fwhm, offset))


    def __del__(self):
        pass

    def run(self):
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", help="PGPLOT device",
            required=False, type=str, default="1/xs")
    args = parser.parse_args()
    app = App(args)

