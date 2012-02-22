#!/usr/bin/env python
# encoding: utf-8


'''
This script plots the data generated
by HighPrecisionRange.py
'''

import cPickle
import os.path
import numpy as np 
import matplotlib.pyplot as plt 

def main():
    """Main program
    @return: @todo
    """

    filename = os.path.join(
            os.path.dirname(__file__),
            "precisiondata.cpickle"
            )

    exptimes, crosspoints, satpoints = cPickle.load(open(filename, 'rb'))

    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    ax.plot(exptimes, crosspoints, 'k--')
    ax.plot(exptimes, satpoints, 'k--')

    ax.fill_between(exptimes, crosspoints, satpoints,
            color='0.9')


    # Invert the y axis
    #ax.set_xscale("log")
    ax.set_ylim(ax.get_ylim()[1], ax.get_ylim()[0])

    ax.set_xlabel("Exposure time / s")
    ax.set_ylabel("I magnitude")
    ax.set_title("High precision (>1mmag precision, not saturating)")



    plt.show()

if __name__ == '__main__':
    main()
