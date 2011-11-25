#!/usr/bin/env python

'''
Calculate the distribution of fractions in the centre pixel for a psf of
given size as the psf is moved away from the centre pixel
'''

from pylab import *
from ppgplot import *
from scipy.integrate import *




'''
Integration test part

Compare the manual integration function with scipy.integrate.dblquad
for a function x**2 + y**2.

The answer should be 6666.67 by hand
'''

def Gaussian2D(y, x, fwhm, offset):
    sigma = fwhm / 2.35
    return exp(-(1./2. * sigma**2) * ((x - offset[0])**2 + (y-offset[1])**2))

def Function(x, y):
    return x**2 + y**2

#def IntegrateFunction(low, high, dx, dy):
    #dA = dx * dy
    #sumval = 0.
    #for y in linspace(low[1], high[1], 1./dy):
        #for x in linspace(low[0], high[1], 1./dx):
            #sumval += Function(x, y) * dA
    #return sumval




# scipy method
fwhm = 1.5
xrangevals = (-2.*fwhm, 2.*fwhm)
yrangevals = (-2.*fwhm, 2.*fwhm) 
N = 100

#x = linspace(-3., 3., 100)
#y = linspace(-3., 3., 100)
#X, Y = meshgrid(x, y)
#z = Gaussian2D(Y, X, fwhm, (0.5, 0.))

xpositions = (xrangevals[1] - xrangevals[0]) * random(N) + xrangevals[0]
ypositions = (yrangevals[1] - yrangevals[0]) * random(N) + yrangevals[0]

pgopen("1/xs")
pgenv(-0.1, sqrt(xrangevals[1]**2 + yrangevals[1]**2), -5, 0, 0, 20)

total = dblquad(Gaussian2D, -Inf, Inf, lambda x: -Inf, lambda x: Inf, args=(fwhm, (0., 0.)))[0]
centre = dblquad(Gaussian2D, -0.25, 0.25, lambda x: -0.25, lambda x: 0.25, args=(fwhm, (0., 0.)))[0]
pgpt(array([0.,]), log10([centre / total,]), 1)
for y in ypositions:
    for x in xpositions:
        r = sqrt(x**2 + y**2)
        centre = dblquad(Gaussian2D, -0.25, 0.25, lambda x: -0.25, lambda x: 0.25, args=(fwhm, (x, y)))[0]
        ratio = centre / total

        # plot the centres
        pgpt(array([r,]), log10([ratio,]), 1)



pgclos()
