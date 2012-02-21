#!/usr/bin/env python
# -*- coding: utf-8 -*-


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
#import pyfits
from Config import *
import AstErrors as ae
#from ppgplot import *



def Banner(text):
    printText = text.upper()
    width = len(text) + 4
    print "-" * width
    print "| %s |" % (printText,)
    print "-" * width




class App(object):
    '''
    Main application object for the project
    '''
    def setUpAssumptions(self):
        # Doing exposures per hour
        self.targettime = TargetBinTime

        # Number of years
        self.nYears = self.args.years

        # Exposure time of science exposures
        self.exptime = self.args.exptime

        if self.exptime <= 0.:
            raise RuntimeError("Exposure time cannot be <= 0")

        # Detector object
        self.NGTSDetector = ae.NGTSDetector()

        # Number of bias/dark frames per day
        # These can be taken during the day so dark time is not needed
        # and therefore are taken every day
        self.nBiasPerDay = 30
        self.nDarkPerDay = 30


        # Number of flat frames per day
        # Flat frames are only taken when the dome is open and therefore
        # must be multiplied by number of good days
        self.nFlatPerDay = 45

        # Number of open hours per year
        # Comes from Joao
        self.nOpenHours = 3264.

        # Image size (MB)
        self.imageSize = 8.5

        # Number of telescopes
        self.nTelescopes = 12

        # Total number of hours per year
        self.nTotalHours = 0.5 * 24. * self.daysInYear()

        # Number of slews per telescope per night
        self.nSlews = 1.

        # Slew time (seconds)
        self.slewTime = 90.
    
    def __init__(self, args):
        '''
        Constructor
        '''
        super(App, self).__init__()
        self.args = args

        # Call the calculation functions
        self.setUpAssumptions()
        self.doCalculation()
        self.printResults()

    def daysInYear(self):
        return 365.25

    def MB(self):
        return 1024**2

    def TB(self):
        return self.MB()**2


    def doCalculation(self):
        #self.readtime = self.NGTSDetector.readTime()
        self.readtime = ReadTime



        # Number of exposures per hour
        self.nExposures = self.targettime / (self.exptime + self.readtime)


        # Fraction of observable nights
        self.nOpenNights = float(self.nOpenHours) / float(self.nTotalHours)

        # Number of science images
        self.nScienceImages = np.ceil(self.nOpenHours * self.nExposures * self.nTelescopes * self.nYears)

        # Each image is this many bytes
        self.imageSizeBytes = self.imageSize * self.MB()

        # Image storage requirements
        self.scienceStorageBytes = self.nScienceImages * self.imageSizeBytes

        # Number of TB the science images will take up
        self.scienceStorage = self.scienceStorageBytes / self.TB()

        # Add in the calibration frames
        self.nTotalBias = self.nBiasPerDay * self.daysInYear() * self.nTelescopes * self.nYears
        self.nTotalDark = self.nDarkPerDay * self.daysInYear() * self.nTelescopes * self.nYears

        # Flat fields are only taken during observable conditions so
        # this needs to be multiplied by the number of open nights
        self.nTotalFlat = self.nFlatPerDay * self.nOpenNights * self.daysInYear() * self.nTelescopes * self.nYears


        # Total number of calibration frames
        self.nCalibFrames = self.nTotalBias + self.nTotalDark + self.nTotalFlat

        # Calibration storage amount
        self.calibStorageBytes = self.nCalibFrames * self.imageSizeBytes
        self.calibStorage = self.calibStorageBytes / self.TB()

        # Total number of frames
        self.nTotalFrames = self.nCalibFrames + self.nScienceImages

        # Convert total frames to total TB
        self.totalStorageBytes = self.nTotalFrames * self.imageSizeBytes
        self.totalStorage = self.totalStorageBytes / self.TB()

        # Calibration frames fraction
        self.calibFraction = self.calibStorageBytes / self.totalStorageBytes


    def printResults(self):
        print 
        Banner("assumptions")
        print 

        print "Exposure time: %.2fs" % (self.exptime,)
        print "Calculating for %.1f year(s)" % (self.nYears,)
        print "%d bias frames per day" % (self.nBiasPerDay,)
        print "%d dark frames per day" % (self.nDarkPerDay,)
        print "Average of %d flat frames per day (on observable nights)" % (self.nFlatPerDay,)
        print "Calculated observable hours: %d" % (self.nOpenHours,)
        print "Simulating for %d telescopes" % (self.nTelescopes,)
        print "Each image is %.1fMB" % (self.imageSize,)
        print "%s" % (self.NGTSDetector,)

        print 
        Banner("Calculation")
        print 


        print "Read time: %.4fs" % (self.readtime,)
        print "%f exposures per hour" % (self.nExposures,)
        print "Total night hours in a year: %d" % (self.nTotalHours,)
        print "Fraction of observable nights per year: %f" % (self.nOpenNights,)
        print "%d science images per year" % (self.nScienceImages)
        print "Science images will take up %.2fTB" % (self.scienceStorage,)
        print "%d bias frames taken" % (np.ceil(self.nTotalBias),)
        print "%d dark frames taken" % (np.ceil(self.nTotalDark),)
        print "%d flat frames taken" % (np.ceil(self.nTotalFlat),)
        print "%d total calibration frames" % (np.ceil(self.nCalibFrames),)
        print "Calibration frames will take up %.2fTB" % (self.calibStorage,)
        print "Calibration frames make up %.3f%% of the total storage" % (
                self.calibFraction * 100.,)

        print 
        Banner("results")
        print 

        print "%d total frames" % (np.ceil(self.nTotalFrames),)
        print "Total storage requirement: %.3fTB" % (self.totalStorage)


if __name__ == '__main__':
    try:
        helpstr = """This program calculates the number of images required to 
        store the NGTS raw data, including the calibration frames and
        science images. The downtime due to exposing each frame is
        accounted for as is the number of good observing nights from
        Paranal (supplied by Joao Bento).
        """

        parser = argparse.ArgumentParser(epilog=helpstr)
        parser.add_argument("exptime", help="Science exposure time",
                type=float)
        parser.add_argument("-y", "--years", help="Number of years to simulate",
                required=False, default=1, type=float)

        args = parser.parse_args()
        app = App(args)
    except RuntimeError as e:
        print >> sys.stderr, "Error:", e
        sys.exit(1)

    except KeyboardInterrupt:
        print >> sys.stderr, "Interrupt caught, exiting..."
        sys.exit(0)
