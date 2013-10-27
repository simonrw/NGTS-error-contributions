#!/usr/bin/env python

import sys
import os
import os.path
import argparse
#from subprocess import Popen, call, PIPE, STDOUT
import matplotlib.pyplot as plt
import numpy as np
import srw
#import pyfits
import logging
import AstErrors as ae
import cPickle
import tables
from Config import *
import csv

logger = logging.getLogger('TheoryNoise')

class FileRender(object):
    def __init__(self, out_filename):
        self.filename = out_filename
        self.datasets = {}

    def add_dataset(self, name, values):
        self.datasets[name.lower()] = values

    def render(self):
        keys = self.datasets.keys()
        values = zip(*self.datasets.values())
        with open(self.filename, 'w') as outfile:
            writer = csv.DictWriter(outfile, keys)
            writer.writeheader()
            for row in values:
                dict = {k: v for (k, v) in zip(keys, row)}
                writer.writerow(dict)


class NullFileRender(object):
    '''
    Allows matplotlib calls on the axis without it existing
    '''
    def __getattr__(self, name):
        '''
        Like Ruby's `method_missing`
        '''
        def fn(*args, **kwargs):
            pass

        return fn


class App(object):
    '''
    Main application object for the project
    '''
    source = []
    sky = []
    read = []
    scin = []
    total = []
    dark = []
    def __init__(self, args):
        '''
        Constructor
        '''
        super(App, self).__init__()
        self.args = args
        self.exptime = self.args.exptime
        logger.info("Exposure time: {:f}".format(self.exptime))

        self.fileDir = os.path.dirname(__file__)

        self.mag = np.linspace(7, 18., 1000)

        self.plotLimits = (self.mag.max(), self.mag.min(),
                -6, -1)

        self.run()

    def plotWASPData(self):
        '''
        Overlays the wasp data from Joao
        '''
        waspdata = cPickle.load(open(
            os.path.join(self.fileDir,
            "JoaoData", "data.cpickle")
            ))

        # Convert I to V
        imagCorrection = 0.27

    def plotNGTSData(self):
        '''
        Overlays the NGTS data
        '''
        ngtsdata = cPickle.load(open(
            os.path.join(self.fileDir,
                "NGTSData", "NGTSData.cpickle")
            ))


    def saturationLimit(self, group):
        fits = cPickle.load(
                open(os.path.join(self.fileDir,
                    "fits.cpickle"))
                )
        self.brightLimit = fits['bright'](np.log10(self.exptime))
        self.darkLimit = fits['dark'](np.log10(self.exptime))


        group._v_attrs.brightlimit = self.brightLimit
        group._v_attrs.darklimit = self.darkLimit

        plt.axvline(self.brightLimit, color='k', ls='-')
        plt.axvline(self.darkLimit, color='k', ls='--')


    def run(self):
        '''
        Main function
        '''
        radius = 2.5  # Radius of flux extraction aperture
        npix = np.pi * radius ** 2
        detector = ae.NGTSDetector()
        extinction = 0.06
        targettime = self.args.totaltime
        height = 2400.
        apsize = 0.2
        airmass = self.args.airmass
        readnoise = ReadNoise
        # zp = srw.ZP(1.)
        zp = 20.6795

        logger.info('Airmass: {:f}'.format(airmass))
        logger.info('Read noise: {:f}'.format(readnoise))
        logger.info('Zero point: {:f}'.format(zp))
        logger.info('Integrating for {:f} seconds'.format(targettime))

        try:
            skypersecperpix = SkyLevel[self.args.skylevel]
            logger.info('Sky level: {:f} electrons per second per pixel'.format(
                skypersecperpix))
        except KeyError:
            raise RuntimeError("Invalid sky type entered")


        dark_level = self.args.darklevel
        for mag in self.mag:
            errob = ae.ErrorContribution(mag, npix, detector.readTime(),
                    extinction, targettime, height, apsize, zp, readnoise)
            self.source.append(errob.sourceError(airmass, self.exptime))
            self.sky.append(errob.skyError(airmass, self.exptime,
                skypersecperpix))
            self.read.append(errob.readError(airmass, self.exptime))
            self.scin.append(errob.scintillationError(airmass, self.exptime))
            self.dark.append(errob.darkError(airmass, self.exptime, dark_level))
            self.total.append(errob.totalError(airmass, self.exptime,
                skypersecperpix, dark_level))

        self.source, self.sky, self.read, self.scin, self.total, self.dark = [
                np.array(d) for d in [self.source, self.sky, self.read, self.scin,
                    self.total, self.dark]]


        if self.args.plotwasp: self.plotWASPData()
        if self.args.plotngts: self.plotNGTSData()

        if args.render:
            fr = FileRender(args.render)
        else:
            fr = NullFileRender()

        outfile = tables.openFile('noisemodel.h5', 'w')
        group = outfile.createGroup('/', 'data', 'Data')
        outfile.createArray(group, 'mag', self.mag)

        # Plot the theory lines
        fr.add_dataset('Magnitude', self.mag)
        for (colour, ydata, label) in zip(
                ['r', 'b', 'g', 'c', 'm', 'k'],
                [self.source, self.sky, self.read, self.scin, self.total, self.dark],
                ['Source', 'Sky', 'Read', 'Scintillation', 'Total', 'Dark']
                ):
            plt.plot(self.mag, ydata, color=colour, ls='-', label=label)
            fr.add_dataset(label, ydata)

            outfile.createArray(group, label.lower(), ydata)
        if self.args.satlimit: self.saturationLimit(group)
        fr.render()

        # Draw the 1mmag line
        plt.axhline(1E-3, color='k', ls=':', zorder=-10)

        # Plot a line at the point when the total error meets
        # the 1mmag line
        distFrom1mmag = np.abs(self.total - 1E-3)
        ind = distFrom1mmag==distFrom1mmag.min()
        self.crossPoint = self.mag[ind][0]
        plt.axvline(self.crossPoint, color='k', ls=':', zorder=-10)

        group._v_attrs.crosspoint = self.crossPoint

        plt.xlabel(r'I magnitude')
        plt.ylabel(r'Fractional error')
        if not args.notitle:
            plt.title(r"$t_e$: %.1f s, "
                        "$t_I$: %.1f hours, "
                        "1mmag @ %.3f mag" % (self.exptime, targettime/3600.,
                            self.crossPoint))

        plt.legend(loc='best')
        plt.yscale('log')
        plt.xlim(18, 6)
        plt.ylim(ymin=1E-5)

        if self.args.verbose:
            print "CROSSPOINT {:.8f}".format(self.crossPoint)
            print "DARK {:.8f}".format(self.darkLimit)
            print "BRIGHT {:.8f}".format(self.brightLimit)

        group._v_attrs.totaltime = targettime
        group._v_attrs.exptime = self.exptime
        outfile.close()

        plt.grid(True, which='both')
        if self.args.output:
            plt.savefig(self.args.output)
        else:
            plt.show()


if __name__ == '__main__':
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", r'.*use PyArray_AsCArray.*')
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument("-t", "--totaltime", help="Total integration time",
                    default=3600., type=float, required=False)
            parser.add_argument("-e", "--exptime", help="Science exposure time",
                    type=float, required=True)
            parser.add_argument("-s", "--skylevel", help="Sky type (bright "
                                "or dark", choices=["bright", "dark"],
                                type=lambda val: val.lower(),
                                required=False, default="dark")
            parser.add_argument('-o', '--output', help='Output device',
                    required=False)
            parser.add_argument("-w", "--plotwasp", help="Overlay some WASP staring data",
                    action="store_true", default=False)
            parser.add_argument("-n", "--plotngts", help="Overlay some NGTS prototype data",
                    action="store_true", default=False)
            parser.add_argument("-S", "--satlimit", help="Do not plot saturation limit",
                    action="store_false", default=True)
            parser.add_argument('-v', '--verbose', help='Verbose mode',
                    required=False, action='store_true')
            parser.add_argument('-T', '--notitle', help='Do not plot the title',
                    action='store_true')
            parser.add_argument('-a', '--airmass', help='Airmass value',
                    default=1.3, type=float, required=False)
            parser.add_argument('-d', '--darklevel', help='Level of dark current (e- per second)',
                    default=0.6, type=float, required=False)
            parser.add_argument('-r', '--render', help="Render data to a csv file",
                    required=False)
            args = parser.parse_args()
            app = App(args)
        except KeyboardInterrupt:
            print >> sys.stderr, "Interrupt caught, exiting..."
            sys.exit(0)
