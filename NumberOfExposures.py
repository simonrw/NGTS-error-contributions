#!/usr/bin/env python

'''
Given an exposure time, and some assumptions about the number
of flat/dark/bias fields made, the number of exposures per hour
can be calculated. 
'''

import sys
#import os
#import os.path
import argparse
#from subprocess import Popen, call, PIPE, STDOUT
#import matplotlib.pyplot as plt
import numpy as np
import srw
#import pyfits
#from ppgplot import *

class Detector(object):
    ccdsize = None
    verttime = None
    horizspeed = None

    def __init__(self, ccdsize, verttime, horizspeed):
        super(Detector, self).__init__()
        self.ccdsize = ccdsize
        self.verttime = verttime
        self.horizspeed = horizspeed

    def readTime(self):
        return self.ccdsize[1] * (self.verttime + self.ccdsize[0] / self.horizspeed)


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
        self.colours = srw.bcolours()
        if self.args.nocolours: self.colours.disable()


        # Doing exposures per hour
        self.targettime = 3600.

        # Exposure time of science exposures
        self.exptime = self.args.exptime
        self.NGTSDetector = Detector([2048, 2048], 38E-6, 3E6)

        print "Exposure time: %s%.2fs%s" % (self.colours.FAIL,
                self.exptime, self.colours.ENDC)

        # Number of bias/dark frames per day
        # These can be taken during the day so dark time is not needed
        # and therefore are taken every day
        self.nBiasPerDay = 30
        self.nDarkPerDay = 30

        print "%d bias frames per day" % (self.nBiasPerDay,)
        print "%d dark frames per day" % (self.nDarkPerDay,)

        # Number of flat frames per day
        # Flat frames are only taken when the dome is open and therefore
        # must be multiplied by number of good days
        self.nFlatPerDay = 45
        print "Average of %d flat frames per day (on observable nights)" % (self.nFlatPerDay,)

        # Number of open hours per year
        # Comes from Joao
        self.nOpenHours = 3264.
        print "Calculated observable hours: %d" % (self.nOpenHours,)

        # Image size (MB)
        self.imageSize = 8.5

        # Number of telescopes
        self.nTelescopes = 12
        print "Simulating for %d telescopes" % (self.nTelescopes,)


        self.run()

    def run(self):
        '''
        Main function
        '''
        readtime = self.NGTSDetector.readTime()



        # Number of exposures per hour
        nExposures = self.targettime / (self.exptime + readtime)
        print "%f exposures per hour" % (nExposures,)

        # Total number of hours per year
        nTotalHours = 0.5 * 24. * 365.25
        print "Total night hours in a year: %d" % (nTotalHours,)

        nOpenNights = float(self.nOpenHours) / float(nTotalHours)
        print "Fraction of observable nights per year: %f" % (nOpenNights,)

        nScienceImages = np.ceil(self.nOpenHours * nExposures * self.nTelescopes)
        print "%d science images per year" % (nScienceImages)

        imageSizeBytes = self.imageSize * 1024 * 1024
        print "Each image is %d bytes, %.1fMB" % (imageSizeBytes, self.imageSize,)

        # Image storage requirements
        scienceStorageBytes = nScienceImages * imageSizeBytes

        scienceStorage = scienceStorageBytes / 1024**4
        print "Science images will take up %.2fTB" % (scienceStorage,)

        # Add in the calibration frames
        nTotalBias = self.nBiasPerDay * 365.25 * self.nTelescopes
        nTotalDark = self.nDarkPerDay * 365.25 * self.nTelescopes
        nTotalFlat = self.nFlatPerDay * nOpenNights * 365.25 * self.nTelescopes

        print "%d bias frames taken" % (nTotalBias,)
        print "%d dark frames taken" % (nTotalDark,)
        print "%d flat frames taken" % (nTotalFlat,)

        nCalibFrames = nTotalBias + nTotalDark + nTotalFlat
        print "%d total calibration frames" % (nCalibFrames,)

        calibStorageBytes = nCalibFrames * imageSizeBytes
        calibStorage = calibStorageBytes / 1024**4
        print "Calibration frames will take up %.2fTB (%.2f%% of science capacity)" % (
                calibStorage, calibStorage * 100. / scienceStorage)

        nTotalFrames = nCalibFrames + nScienceImages
        print "%s%d%s total frames" % (self.colours.FAIL, nTotalFrames,
                self.colours.ENDC)

        totalStorageBytes = nTotalFrames * imageSizeBytes
        totalStorage = totalStorageBytes / 1024**4
        print "Total storage requirement: %s%.3fTB%s" % (self.colours.FAIL,
                totalStorage, self.colours.ENDC)



if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("exptime", help="Science exposure time",
                type=float)
        parser.add_argument("-c", "--nocolours", help="Do not use coloured output",
                action="store_true", default=False)

        args = parser.parse_args()
        app = App(args)
    except KeyboardInterrupt:
        print >> sys.stderr, "Interrupt caught, exiting..."
        sys.exit(0)
