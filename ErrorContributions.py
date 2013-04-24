#!/usr/bin/env python
# -*- coding: utf-8 -*-

from numpy import *
import matplotlib.pyplot as plt
import pyximport; pyximport.install()
import argparse
from scipy.integrate import dblquad
import Config as config
import tables

def Gaussian2D(y, x, fwhm, offset):
    sigma = fwhm / 2.35
    arg1 = (x-offset[0])**2
    arg2 = (y - offset[1])**2
    return exp(-(arg1 + arg2) / (2. * sigma**2))

# The colours
colours = {
        'red': 2,
        'black': 1,
        'green': 3,
        'blue': 4,
        'cyan': 5,
        }

# Some constants

# Read noise electrons have to be added in quadrature
ReadNoisePerAperture = config.ReadNoise * sqrt(config.Area) # electrons
AirmassOptions = [1., 2.]
Extinction = 0.06 # magnitudes per airmass

r'''
Note: errors in quadrature

If the source counts are summed then the errors on the
relevant parameters are added in quadrature for each
frame that goes into the binning calculation.

The net result of this is that if the error in one
frame is \sigma_i then the total error in quadrature is

\sigma_T = \sqrt{\sigma_1^2 + \sigma_2^2 + ...}
    = \sqrt{N \sigma_i**2}
    = \sqrt{N} * \sigma_i
'''

def ZP(etime):
    """Zero point for NGTS data scaled by exposure time.

    Decided not to include a default value as this will cause
    troubles.

    Derivation
    ----------

    If f is the base flux and f' the flux at a greater exposure time,
    for the two measurements to give the same zero point, the equation

    m = m_0,1 - 2.5*log10(f) = m_0,2 - 2.5*log10(f')

    m_0,2 - m_0,1 = 2.5*log10(f') - 2.5*log10(f)
                  = 2.5*[log10(f') - log10(f)]
                  = 2.5*log10(f' / f)

    if f' = t*f where t is the ratio of exposure times then

    m_0,2 - m_0,1 = 2.5*log10(t)

    so m_0,2 = m_0,1 + 2.5*log10(t)

    """
    zp_40 = 24.51
    ref_exp = 40.
    zp = zp_40 + 2.5*log10(etime / ref_exp)

    return zp


def Scintillation(t, Airmass):
    '''
    Scintillation function

    Takes the exposure time and scales this by the
    parameters for the NGTS telescope.

    Aperture radius = 20cm
    Assume an airmass of 1
    Height of Paranal = 2400m
    '''
    ApertureSize = 0.2
    Height = 2400.
    mscin = 0.004 * ApertureSize**(-2./3.) * Airmass**(7./4.) * exp(-Height/8000.) * (2. * t) ** (-1./2.)
    error_value = 1. - (10 ** (-mscin / 2.5))
    return error_value


def main(args):
    Moon = args.skylevel  # options are bright or dark

    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Print some nice stuff to the console
    print "Assuming a gain of %.1f" % config.Gain
    print "Bias level: %.2f electrons" % config.BiasLevel
    print "FWHM: %.2f pixels" % config.FWHM
    print "Aperture radius: %.2f pixels" % config.Radius
    print "Aperture area: %.2f pixels" % config.Area
    print "Read noise per aperture: %.2f electrons" % ReadNoisePerAperture
    print "Simulating to %.1f hour(s)" % (config.TargetBinTime / 3600.,)
    print "Full well depth set to %dk electrons" % (config.FullWellDepth / 1000)

    # Target magnitude
    TargetMag = args.targetmag
    print "Target magnitude: %.2f" % TargetMag

    # Central pixel fraction (calculated at runtime)
    '''
    Taken from the ratio between two gaussian integrals:
        * The integral of flux in the central pixel
        * The integral to infinity of the psf

    This is calculated by rastering a psf across a pixel and
    picking the most common value.
    '''
    #CentralPixelFraction = dblquad(Gaussian2D, -0.5, 0.5, lambda x: -0.5, lambda x: 0.5, args=(FWHM, (0., 0.)))[0] / \
            #dblquad(Gaussian2D, -Inf, Inf, lambda x: -Inf, lambda x: Inf, args=(FWHM, (0., 0.)))[0]
    CentralPixelFraction = 0.281838
    print "Central pixel fraction: %f"  %  CentralPixelFraction

    # science exposure time (equal in log space)
    expTime = 10**linspace(log10(5), log10(3600), 100)

    # total frame duration (exposure + readout)
    totalFrameTime = expTime + config.ReadTime
    print "Readout time at %.1f MHz: %f seconds" % (config.HorizontalSpeed / 1E6, config.ReadTime)

    # Number of exposures that fit into an hour
    nExposures = config.TargetBinTime / totalFrameTime

    line_styles = ['-', '--', ':']
    for i, Airmass in enumerate(AirmassOptions):
        print "\t\t*** AIRMASS %.1f ***" % Airmass;
        # Airmass correction factor
        AirmassCorrection = 10**((Extinction * Airmass) / 2.5)
        print "Airmass correction factor: %.5f" % AirmassCorrection

        ###############################################################################
        #                               Source Error
        ###############################################################################

        # Zero point for a 1s exposure (true zero point)
        if args.zeropoint:
            zp = float(args.zeropoint)
        else:
            zp = ZP(1.)
        print "Instrumental zero point: %.5f mag" % zp

        # Correct the source magnitude for airmass
        AirmassCorrectedMag = TargetMag + Extinction * Airmass
        print "Airmass corrected magnitude: %.3f" % AirmassCorrectedMag


        # Number of source photons
        SourceCountsPerSecond = 10**((zp - AirmassCorrectedMag) / 2.5)
        print "Source has %.1f electrons per second" % SourceCountsPerSecond
        SourceCounts = SourceCountsPerSecond * expTime

        # binned source counts
        BinnedSourceCounts = SourceCounts * nExposures

        #Error due to the source
        SourceError = sqrt(BinnedSourceCounts)

        ###############################################################################
        #                               Read Noise Error
        ###############################################################################


        # Read noise error
        # Must add the read noise errors in quadrature
        # for each exposure
        ReadNoiseError = ReadNoisePerAperture * sqrt(nExposures)

        ###############################################################################
        #                               Sky Error
        ###############################################################################


        # Correct the sky in 40 seconds value
        #CorrectedSkyIn40Seconds = SkyIn40Seconds

        ## Get the sky counts per pixel per second
        #SkyPerSecPerPix = CorrectedSkyIn40Seconds / SkyExposure
        if Moon.lower() == "bright": SkyPerSecPerPix = 160. # 50 for dark time, 160 for bright time
        elif Moon.lower() == "dark": SkyPerSecPerPix = 50.
        print "Sky has %.1f electrons per second per pixel" % SkyPerSecPerPix

        # Sky counts per second
        SkyPerSec = SkyPerSecPerPix * config.Area
        print "Sky has %.1f electrons per second" % SkyPerSec

        # Total sky counts per exposure
        SkyCounts = SkyPerSec * expTime


        # Binned sky counts
        BinnedSkyCounts = SkyCounts * nExposures

        # Sky Error
        SkyError = sqrt(BinnedSkyCounts)

        ###############################################################################
        #                               Scintillation Error
        ###############################################################################

        # scintillation error per source count
        FractionalScintillationError = Scintillation(expTime, Airmass)

        # Scale up by the source counts
        ScintillationErrorPerExposure = FractionalScintillationError * SourceCounts

        # Add the errors in quadrature when binning
        ScintillationError = ScintillationErrorPerExposure * sqrt(nExposures)


        ###############################################################################
        #                               Total Error
        ###############################################################################

        TotalError = sqrt(SourceError**2 + ReadNoiseError**2 + SkyError**2 + ScintillationError**2)


        ###############################################################################
        #                               Saturation
        ###############################################################################

        '''
        From previous calculation, for the worst case when the psf is centred
        on the pixel, 30% of the flux goes into that pixel. Therefore when 30%
        of the total flux (source + sky) reaches the full well depth then the
        central pixel is saturatied

        The 30% is assuming a psf fwhm of 1.5 pixels, and the result is calculated
        in the variable: CentralPixelFraction
        '''
        TotalFrameCounts = SourceCounts + SkyCounts + (config.BiasLevel * config.Area)

        # Multiply by the fraction that is in the central pixel
        FluxInCentralPixel = CentralPixelFraction * TotalFrameCounts

        # Get the exposure times at which the source is saturated
        SaturatedExpTimes = expTime[FluxInCentralPixel > config.FullWellDepth]

        # Pick the minimum one to find the saturation point
        SaturatedLevel = SaturatedExpTimes.min()

        print "Saturation in %.2f seconds" % SaturatedLevel


        ###############################################################################
        #                               Plotting
        ###############################################################################



        # add the data lines
        if i == 0:
            ax.plot(expTime, SourceError / BinnedSourceCounts, 'r-',
                    ls=line_styles[i], label="Source")
            ax.plot(expTime, ReadNoiseError / BinnedSourceCounts, 'c-',
                    ls=line_styles[i], label="Read")
            ax.plot(expTime, SkyError / BinnedSourceCounts, 'b-',
                    ls=line_styles[i], label="Sky")
            ax.plot(expTime, ScintillationError / BinnedSourceCounts, 'g-',
                    ls=line_styles[i], label="Scintillation")
            ax.plot(expTime, TotalError / BinnedSourceCounts, 'k-',
                    ls=line_styles[i], label="Total")
        else:
            ax.plot(expTime, SourceError / BinnedSourceCounts, 'r-',
                    ls=line_styles[i])
            ax.plot(expTime, ReadNoiseError / BinnedSourceCounts, 'c-',
                    ls=line_styles[i])
            ax.plot(expTime, SkyError / BinnedSourceCounts, 'b-',
                    ls=line_styles[i])
            ax.plot(expTime, ScintillationError / BinnedSourceCounts, 'g-',
                    ls=line_styles[i])
            ax.plot(expTime, TotalError / BinnedSourceCounts, 'k-',
                    ls=line_styles[i])

    # Plot the saturated line
    ax.axvline(SaturatedLevel, color='k', ls=':')

    # label the graph
    plt.legend(loc='best')
    ax.set_xlabel(r'Exposure time / s')
    ax.set_ylabel(r'Fractional error')

    # Create the plot
    ax.set_xscale('log')
    ax.set_yscale('log')
    # ax.set_ylim(1E-6, 3E-3)
    plt.show()



if __name__ == '__main__':
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", r'.*use PyArray_AsCArray.*')
        parser = argparse.ArgumentParser()
        parser.add_argument('-d', '--device',
                            help='Plotting device', default='1/xs',
                            required=False, type=str,
                            metavar='PGPLOT device')
        parser.add_argument('-m', '--targetmag',
                            help="Target magnitude", default=None,
                            type=float, metavar='magnitude',
                            required=True)
        parser.add_argument("-s", "--skylevel", help="Sky type (bright "
                            "or dark", choices=["bright", "dark"],
                            type=lambda val: val.lower(),
                            required=False, default="dark")
        parser.add_argument('-z', '--zeropoint', help='Custom zero point',
                            required=False, default=None)
        args = parser.parse_args()



        main(args)
