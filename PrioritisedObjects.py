#!/usr/bin/env python
# encoding: utf-8

'''
Assign a weight to each object
for a specific exposure time and count up
the total sum for each exposure time.

The hightest weight wins
'''

import NHighPrecisionObjects
import numpy as np
import argparse
from ppgplot import *

def calc_weight(mag, t, bonus, importance=[0.05,  0.3, 1.]):
    '''
    Weight is inversely proportional to the magnitude
    ie brighter objects are more important

    Add a value if the target is in the high precision
    range, and subtract a value if the target is saturated
    '''
    rangeVals = NHighPrecisionObjects.rangeAtExptime(t)
    saturated = mag < rangeVals[0]
    highprecision = (mag <= rangeVals[1]) & (np.logical_not(saturated))

    weight = np.poly1d(importance)(mag.max() - mag)
    weight[saturated] -= bonus
    weight[highprecision] += bonus

    return weight


def main(args):
    parser = NHighPrecisionObjects.NOMADDataStore()

    bonus = 15
    importance = [1., 0.]

    linestyles = [1, 2, 3]

    if args.output:
        pgopen(args.output)
    else:
        pgopen("/xs")

    exptime_hist = []
    weights_hist = []
    for i, field in enumerate([1, 2, 3]):
        parser.setField(field)
        objects = parser.visible()
        exptime, weights = zip(*[
            (e, np.sum(calc_weight(objects, e, bonus=bonus, importance=importance)))
            for e in np.linspace(5, 90, 150)])

        exptime_hist.append(exptime)
        weights_hist.append(weights)

    exptime_hist = map(np.array, exptime_hist)
    weights_hist = map(np.array, weights_hist)

    offset = 0.01
    plot_min = np.log10(np.min(weights_hist)) - offset
    plot_max = np.log10(np.max(weights_hist)) + offset
    pgenv(0, np.max(exptime_hist) + 10, plot_min, plot_max, 0, 0)

    for i, (exptime, weight) in enumerate(zip(exptime_hist, weights_hist)):
        pgsls(linestyles[i])
        pgline(np.array(exptime), np.log10(weight))
        pgsls(1)


    # Get the peak value
    pgsls(4)

    peak_value = exptime_hist[0][weights_hist[0] == weights_hist[0].max()][0]
    pgline(np.array([peak_value, peak_value]), np.array([plot_min, plot_max]))
    pgsls(1)

    pglab(r"Exposure time / s", r"log10 weight", r"Peak exptime: %.1f seconds" %
            peak_value)

    # Create the legend
    pgsvp(0.7, 0.9, 0.725, 0.875)
    pgswin(0, 1, 0, 1)
    #pgbox("BC", 0, 0, "BC", 0, 0)
    pgbox("", 0, 0, "", 0, 0)

    y = [0.8, 0.5, 0.2]
    for i in xrange(len(linestyles)):
        pgsls(linestyles[i])
        pgline(np.array([0.2, 0.4]), np.ones(2) * y[i])
        pgtext(0.5, y[i], "NOMAD %d" % (i + 1, ))

    #pgbox("", 0, 0, "", 0, 0)



        #plt.plot(exptime, np.log10(weights), color='k', ls=linestyles[i],
                #label="NOMAD %d" % field)
    #plt.xlabel("Exposure time / s")
    #plt.ylabel("log10 Weight")

    parser.close()
    #plt.title("Max at %.2fs" % exptime[weights==weights.max()])
    #plt.legend(loc='best')

    pgclos()
    #if args.output:
        #plt.savefig(args.output)
    #else:
        #plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", type=str,
            help="Output plot", default=None, required=False)
    args = parser.parse_args()
    main(args)
