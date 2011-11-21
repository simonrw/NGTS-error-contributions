#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Plot import *
from numpy import *
import pyximport; pyximport.install()
import argparse
import GaussianIntegrals as GI

# The colours
colours = {
        'red': 2,
        'black': 1,
        'green': 3,
        'blue': 4,
        'cyan': 5,
        }

# Some constants
HorizontalSpeed = 3E6
VerticalTime = 38E-6
NAXIS1 = 2048
NAXIS2 = 2048
ReadTime = NAXIS2 * (VerticalTime + NAXIS1 / HorizontalSpeed) # seconds
ReadNoise = 11.7 # e- per pix
FWHM = 1.5
Radius = 1.5 * FWHM # pixels
Area = pi * Radius**2

# Read noise electrons have to be added in quadrature 
ReadNoisePerAperture = ReadNoise * sqrt(Area) # electrons
Digitisation = 16
SkyIn40Seconds = 1700.
SkyExposure = 40.
ElectronicSatur = ((2**Digitisation - 1)) * Area
TargetBinTime = 3600.
FullWellDepth = 150000
Airmass = 1.
Extinction = 0.04 # magnitudes per airmass

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


def Scintillation(t):
    '''
    Scintillation function

    Takes the exposure time and scales this by the 
    parameters for the NGTS telescope.

    Aperture radius = 20cm
    Assume an airmass of 1
    Height of Paranal = 2400m
    '''
    ApertureSize = 0.2
    Airmass = 1.
    Height = 2400.
    return 0.004 * ApertureSize**(-2./3.) * Airmass**(7./4.) * exp(-Height/8000.) * (2. * t) ** (-1./2.)


def main(args):
    # Print some nice stuff to the console
    print "FWHM: %.2f pixels" % FWHM
    print "Aperture radius: %.2f pixels" % Radius
    print "Aperture area: %.2f pixels" % Area
    print "Read noise per aperture: %.2f electrons" % ReadNoisePerAperture
    print "Simulating to %.1f hour(s)" % (TargetBinTime / 3600.,)
    print "Full well depth set to %dk electrons" % (FullWellDepth / 1000)

    # Target magnitude
    TargetMag = args.targetmag
    print "Target magnitude: %.2f" % TargetMag

    # Central pixel fraction (calculated at runtime)
    '''
    Taken from the ratio between two gaussian integrals:
        * The integral of flux in the central pixel
        * The integral to infinity of the psf

    This is calculated using the PyIntegrate function 
    (which is cython code), and calculates this 
    ratio
    '''
    # Integration constants
    dx, dy = 0.01, 0.01

    # "To infinity" limits
    FakeInfinity = 10.
    CentralPixelFraction = GI.PyIntegrate(FWHM, dx, dy, 0., 0.5) / \
            GI.PyIntegrate(FWHM, dx, dy, 0, FakeInfinity)
    print "Central pixel fraction: %f"  %  CentralPixelFraction

    # science exposure time (equal in log space)
    expTime = 10**linspace(log10(5), log10(3600), 100)

    # total frame duration (exposure + readout)
    totalFrameTime = expTime + ReadTime
    print "Readout time at %.1f MHz: %f seconds" % (HorizontalSpeed / 1E6, ReadTime)

    # Number of exposures that fit into an hour
    nExposures = TargetBinTime / totalFrameTime

    # Airmass correction factor
    AirmassCorrection = 10**((Extinction * (Airmass - 1.)) / 2.5)
    print "Airmass correction factor: %.5f" % AirmassCorrection

    ###############################################################################
    #                               Source Error
    ###############################################################################

    # Zero point for a 1s exposure (true zero point)
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


    # Get the sky counts per pixel per second
    SkyPerSecPerPix = SkyIn40Seconds / SkyExposure
    print "Sky has %.1f electrons per second per pixel" % SkyPerSecPerPix

    # Sky counts per second
    SkyPerSec = SkyPerSecPerPix * Area
    print "Sky has %.1f electrons per second" % SkyPerSec

    # Total sky counts per exposure
    SkyCounts = SkyPerSec * expTime

    # Airmass correct the sky counts
    SkyCounts *= AirmassCorrection

    # Binned sky counts
    BinnedSkyCounts = SkyCounts * nExposures

    # Sky Error
    SkyError = sqrt(BinnedSkyCounts)

    ###############################################################################
    #                               Scintillation Error
    ###############################################################################

    # scintillation error per source count
    FractionalScintillationError = Scintillation(expTime)

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
    TotalFrameCounts = SourceCounts + SkyCounts

    # Multiply by the fraction that is in the central pixel
    FluxInCentralPixel = CentralPixelFraction * TotalFrameCounts

    # Get the exposure times at which the source is saturated
    SaturatedExpTimes = expTime[FluxInCentralPixel>FullWellDepth]

    # Pick the minimum one to find the saturation point
    SaturatedLevel = SaturatedExpTimes.min()

    print "Saturation in %.2f seconds" % SaturatedLevel


    ###############################################################################
    #                               Plotting
    ###############################################################################


    # Plotting class
    Plotter = PlotClass(args.device)

    # add the data lines
    Plotter.addLine({'xdata': expTime, 'ydata': SourceError / BinnedSourceCounts,
        'label': "Source", 'colour': colours['red'], 'ls': 1})
    Plotter.addLine({'xdata': expTime, 'ydata': ReadNoiseError / BinnedSourceCounts,
        'label': "Read noise", 'colour': colours['cyan'], 'ls': 1})
    Plotter.addLine({'xdata': expTime, 'ydata': SkyError / BinnedSourceCounts,
        'label': "Sky", 'colour': colours['blue'], 'ls': 1})
    Plotter.addLine({'xdata': expTime, 'ydata': ScintillationError / BinnedSourceCounts,
        'label': "Scintillation", 'colour': colours['green'], 'ls': 1})
    Plotter.addLine({'xdata': expTime, 'ydata': TotalError / BinnedSourceCounts,
        'label': "Total", 'colour': colours['black'], 'ls': 1})

    # Plot the saturated line
    Plotter.line(SaturatedLevel, direction='y')

    # label the graph
    Plotter.setLabels("Frames", "Fractional error", "Magnitude %.1f star" % args.targetmag)

    # Set up the limits
    Plotter.yrange(log10(1E-6), log10(3E-4))




    # Create the plot
    Plotter.render()

    

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
        args = parser.parse_args()


        main(args)
