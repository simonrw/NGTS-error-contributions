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
import matplotlib.pyplot as plt

def weight(mag, t, bonus, importance=[0.05,  0.3, 1.]):
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

    linestyles = ['-', '--', ':']

    for i, field in enumerate([1, 2, 3]):
        parser.setField(field)
        objects = parser.visible()
        exptime, weights = zip(*[
            (e, np.sum(weight(objects, e, bonus=bonus, importance=importance))) 
            for e in np.linspace(5, 90, 150)])


        plt.plot(exptime, np.log10(weights), color='k', ls=linestyles[i],
                label="NOMAD %d" % field)
        plt.xlabel("Exposure time / s")
        plt.ylabel("log10 Weight")

    parser.close()
    #plt.title("Max at %.2fs" % exptime[weights==weights.max()])
    plt.legend(loc='best')

    if args.output:
        plt.savefig(args.output)
    else:
        plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", type=str, 
            help="Output plot", default=None, required=False)
    args = parser.parse_args()
    main(args)
