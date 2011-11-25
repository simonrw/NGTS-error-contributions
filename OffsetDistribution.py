#!/usr/bin/env python

'''
Calculate the distribution of fractions in the centre pixel for a psf of
given size as the psf is moved away from the centre pixel
'''

from pylab import *
from ppgplot import *
from scipy.integrate import *

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
    def __init__(self):
        super(App, self).__init__()

        self.run()

    def run(self):
        pass
        

if __name__ == '__main__':
    app = App()

