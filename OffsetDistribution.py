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
from Config import *
import matplotlib.pyplot as plt


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
        self.fwhm = FWHM
        self.N = self.args.niter

        self.xRange = [-0.5, 0.5]
        self.yRange = [-0.5, 0.5]


        self.run()

    def Integrate(self, lims, offset):
        return dblquad(Gaussian2D, lims[0], lims[1], lambda x: lims[2], lambda x: lims[3], args=(self.fwhm, offset))


    def run(self):
        # The total integral of a 2d Gaussian to infinity in each direction
        total = self.Integrate((-np.Inf, np.Inf, -np.Inf, np.Inf), (0., 0.))[0]

        fractions = []
        pb = progressbarClass(self.N)
        counter = 0


        # Main loop
        while counter < self.N:
            # Pick two random coordinates
            x = (self.xRange[1] - self.xRange[0]) * np.random.ranf() + self.xRange[0]
            y = (self.yRange[1] - self.yRange[0]) * np.random.ranf() + self.yRange[0]




            # Integrate the new offset Gaussian in the centre pixel and take the fraction
            Fraction = self.Integrate((-0.5, 0.5, -0.5, 0.5), (x, y))[0] / total

            # Add the result to the list
            fractions.append(Fraction)
            pb.progress(counter+1)
            counter += 1


        # Log the fractions
        # Makes the plot easier to read
        fractions = np.log10(fractions)


        # Create the histogram
        vals, edges = np.histogram(fractions, bins=50, range=(-1, 0))

        # Counting errors
        errs = np.sqrt(vals)

        # Width of a bin
        binWidth = np.diff(edges)[0]

        # Normalise the histogram
        # I realise that the numpy.histogram function inclues a density parameter which
        # achieves the same thing but I need the errors from the raw values
        Integral = float(np.sum(vals))

        # Divide the values by the integral of the system
        normalisedVals = vals / Integral
        normalisedErrs = errs / Integral

        # Get the bin centres
        centres = edges[:-1] + binWidth / 2.

        # Print a line at the most probable value
        MostProbable = 10 ** centres[normalisedVals==normalisedVals.max()][0]

        fig = plt.figure()
        ax = fig.add_subplot(111)

        # Plot the histogram
        ax.plot(10 ** centres, normalisedVals, 'k-', drawstyle='steps-mid')

        ax.set_xlabel(r'Fraction')
        ax.set_ylabel(r'Probability')
        ax.set_xscale('log')

        ticks = [0.1, 0.2, 0.5, 1]
        ax.set_xticks(ticks)
        ax.set_xticklabels(ticks)

        ax.axvline(MostProbable, color='k', ls=':', zorder=-10)

        plt.show()




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", help="PGPLOT device",
            required=False, type=str, default="1/xs")
    parser.add_argument("-N", "--niter", help="Number of iterations (use > 5000)",
            required=False, type=int, default=5000)
    args = parser.parse_args()
    app = App(args)

