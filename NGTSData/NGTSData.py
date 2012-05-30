#!/usr/bin/env python
# encoding: utf-8


import sys
#import os
#import os.path
import argparse
#from subprocess import Popen, call, PIPE, STDOUT
import numpy as np
import srw
import pyfits
#from ppgplot import *
import cPickle


class App(object):
    '''
    Main application object for the project
    '''
    def __init__(self, args):
        '''
        Constructor
        '''
        super(App, self).__init__()
        self.args = args
        self.filename = self.args.filename
        self.binwidth = 1. / 24.  # 1 hour bins

        with pyfits.open(self.filename) as f:
            self.flux = f['flux'].data
            self.fluxerr = f['fluxerr'].data
            self.jd = f['hjd'].data

            header = f[0].header
            try:
                self.exptime = float(header['exptime'])
            except KeyError:
                print "Cannot read exposure time, assuming 30 seconds"
                self.exptime = 30

        self.run()

    def run(self):
        '''
        Main function
        '''

        jdmin = self.jd.min()
        jdmax = self.jd.max()

        wav = []
        sd = []

        ledge = np.arange(jdmin, jdmax, self.binwidth)

        for i in range(self.flux.shape[0]):
            binnedLC = []
            for l in ledge:
                r = l + self.binwidth

                ind = (self.jd[i] >= l) & (self.jd[i] < r)
                selectedFlux = self.flux[i, ind]
                selectedFluxErr = self.fluxerr[i, ind]
                binnedLC.append(np.average(selectedFlux,
                    weights=1. / selectedFluxErr ** 2))

            wav.append(np.average(binnedLC))
            sd.append(np.std(binnedLC))

        wav = np.array(wav)
        sd = np.array(sd)

        mag = srw.ZP(self.exptime) - 2.5 * np.log10(wav)

        with open("NGTSData.cpickle", 'w') as pickle_file:
            cPickle.dump({'mag': mag, 'sd': sd / wav}, pickle_file,
                    protocol=2)


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("filename")

        args = parser.parse_args()
        app = App(args)
    except KeyboardInterrupt:
        print >> sys.stderr, "Interrupt caught, exiting..."
        sys.exit(0)
