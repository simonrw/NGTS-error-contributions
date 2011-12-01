'''
Module for calculating the errors for NGTS

This is technically applicable to other projects 
as well but (may) contains some specifics
'''

import unittest2
import numpy as np
from srw import ZP


def sourceError(expTime, mag, zp, readTime, totalTime, airmass,
        extinction):
    '''
    Function takes a magnitude mag object and calculates
    the amount of flux the instrument would recieve for 
    a given exposure time and returns the fractional error 
    value
    '''
    nExposures = totalTime / (expTime + readTime)

    fluxPerImage = 10**((zp - mag)/2.5) + extinction * airmass
    fluxPerImage *= expTime
    totalFlux = fluxPerImage * nExposures
    fluxError = np.sqrt(totalFlux)

    return fluxError / totalFlux

def scintillationError(mag, zp, npix, readTime, airmass, extinction, height, expTime, targetTime, apsize):
    '''
    Returns the extinction as per Southworth 2008
    '''
    nExposures = targetTime / (expTime + readTime)
    errorPerImage = 0.004 * apsize**(-2./3.) * airmass**(7./4.) * \
            np.exp(-height / 8000.) * (2. * expTime)**(-1./2.)

    flux = 10**((zp - mag)/2.5) + extinction * airmass
    flux *= expTime
    totalErrorPerImage = errorPerImage * flux



    totalError = np.sqrt(nExposures) * totalErrorPerImage
    totalFlux = flux * nExposures

    result = totalError / totalFlux
    return result

def readError(mag, zp, readTime, readNoise, npix, expTime, targetTime, extinction,
        airmass):
    '''
    Returns the read error
    '''
    nExposures = targetTime / (expTime + readTime)
    flux = 10**((zp - mag)/2.5) + extinction * airmass
    flux *= expTime
    totalFlux = flux * nExposures

    readNoisePerAperture = np.sqrt(npix) * readNoise
    totalError = np.sqrt(nExposures) * readNoisePerAperture

    return totalError / totalFlux

def skyError(mag, zp, readTime, skypersecperpix, npix, expTime, targetTime, airmass, extinction):
    nExposures = targetTime / (expTime + readTime)
    skyPerSec = npix * skypersecperpix
    skyCounts = skyPerSec * expTime
    skyError = np.sqrt(skyCounts * nExposures)

    flux = 10**((zp - mag)/2.5) + extinction * airmass
    flux *= expTime
    totalFlux = flux * nExposures

    result = skyError / totalFlux
    return result

class ErrorContribution(object):
    '''
    Error class

    Create with the following parameters:

        * Magnitude of object of interest
        * Number of pixels in the aperture
        * Exposure time of the image
        * Time it takes to read the frame, can be 0
        * Extinction coefficient for your filter, can be 0
        * Target time: total coadding time
        * Observatory altitude
        * Aperture (of telescope)
        * Instrumental zero point

    Then the following sources of noise can be calculated for a given 
    airmass, and the fractional errors returned:

        * sourceError - Error from the source
        * scintillationError - Error from scintillation 
        * skyError - Error from the sky background, requires sky background
                    level in photons per pixel per second
        * readError - Error from reading the frame
        * totalError - Combined errors from each source in quadrature

    Each method requires the airmass and exposure time for a given observation,
    and the sky and total methods require the sky background level in sky
    photons per second per pixel.

    As each method returns the fractional value, the flux recieved for a single
    exposure is given by the flux method.
    '''
    def __init__(self, mag, npix, readtime, extinction,
            targettime, height, apsize, zp, readnoise):
        '''
        '''
        super(ErrorContribution, self).__init__()
        self.mag = mag
        self.npix = npix
        self.readtime = readtime
        self.extinction = extinction
        self.targettime = targettime
        self.height = height
        self.apsize = apsize
        self.zp = zp
        self.readnoise = readnoise

    def flux(self, airmass, exptime):
        '''
        Returns the flux for a given magnitude
        '''
        fluxPerImage = 10**((self.zp - mag)/2.5) + self.extinction * airmass
        fluxPerImage *= exptime
        return fluxPerImage

    def totalFlux(self, airmass, exptime):
        '''
        Returns the total flux binned up to targettime for a 
        given observation
        '''
        nExposures = self.targettime / (exptime + self.readtime)
        return self.flux(airmass, exptime) * nExposures



    def sourceError(self, airmass, exptime):
        '''
        '''
        return sourceError(exptime, self.mag, self.zp, self.readtime,
                self.targettime, airmass, self.extinction)

    def scintillationError(self, airmass, exptime):
        '''
        '''
        return scintillationError(self.mag, self.zp, self.npix, self.readtime, 
                airmass, self.extinction, self.height, exptime, 
                self.targettime, self.apsize)

    def readError(self, airmass, exptime):
        '''
        '''
        return readError(self.mag, self.zp, self.readtime, self.readnoise, self.npix,
                exptime, self.targettime, self.extinction, airmass)

    def skyError(self, airmass, exptime, skypersecperpix):
        '''
        '''
        return skyError(self.mag, self.zp, self.readtime, skypersecperpix, 
                self.npix, exptime, self.targettime, airmass, 
                self.extinction)

    def totalError(self, airmass, exptime, skypersecperpix):
        '''
        '''
        source = self.sourceError(airmass, exptime)
        scin = self.scintillationError(airmass, exptime)
        read = self.readError(airmass, exptime)
        sky = self.skyError(airmass, exptime, skypersecperpix)

        return np.sqrt(source**2 + scin**2 + read**2 + sky**2)



class _TestingClass(unittest2.TestCase):
    def setUp(self):
        mag = 9.
        npix = 1.5**4 * np.pi
        self.exptime = 100.
        readtime = 2048. * (38E-6 + 2048. / 3E6)
        extinction = 0.06
        targettime = 3600.
        height = 2400.
        apsize = 0.2
        self.airmass = [1., 2.]
        zp = ZP(1.)
        readnoise = 11.7

        self.errclass = ErrorContribution(
                    mag, npix, readtime, extinction, 
                    targettime, height, apsize, zp, readnoise)

    def test_source_error(self):
        for airmass in self.airmass:
            result = self.errclass.sourceError(airmass, self.exptime)
            lowLim = 8E-5
            upLim = 9E-5
            self.assertGreater(result, lowLim)
            self.assertLess(result, upLim)

    def test_read_error(self):
        for airmass in self.airmass:
            result = self.errclass.readError(airmass, self.exptime)
            lowLim = 1.5E-6
            upLim = 3E-6
            self.assertGreater(result, lowLim)
            self.assertLess(result, upLim)

    def test_sky_error(self):
        for airmass in self.airmass:
            result = self.errclass.skyError(airmass, 50.)
            lowLim = 1E-5
            upLim = 2E-5
            self.assertGreater(result, lowLim)
            self.assertLess(result, upLim)

    def test_scintillation_error(self):
        airmass = 1.
        result = self.errclass.scintillationError(airmass)
        lowLim = 1E-4
        upLim = 2E-4
        self.assertGreater(result, lowLim)
        self.assertLess(result, upLim)

        airmass = 2.
        result = self.errclass.scintillationError(airmass)
        lowLim = 3E-4
        upLim = 4E-4
        self.assertGreater(result, lowLim)
        self.assertLess(result, upLim)

    def test_total_error(self):
        airmass = 1.
        result = self.errclass.totalError(airmass, 11.7, 50.)
        lowLim = 1E-4
        upLim = 2E-4
        self.assertGreater(result, lowLim)
        self.assertLess(result, upLim)
        

        airmass = 2.
        result = self.errclass.totalError(airmass, 11.7, 50.)
        lowLim = 3E-4
        upLim = 4E-4
        self.assertGreater(result, lowLim)
        self.assertLess(result, upLim)






class _Testing(unittest2.TestCase):
    def setUp(self):
        self.readTime = 2048. * (38E-6 + 2048. / 3E6)
        self.totalTime = 3600.
        self.expTime = 1000.
        self.extinction = 0.06
        self.zp = ZP(1.)

    def test_source_error(self):
        mag = 9.
        airmass = 1.

        result = sourceError(self.expTime, mag, self.zp, self.readTime, self.totalTime,
                airmass, self.extinction)
        lowLim = 8E-5
        upLim = 9E-5
        self.assertGreater(result, lowLim)
        self.assertLess(result, upLim)

        airmass = 2.

        result = sourceError(self.expTime, mag, self.zp, self.readTime, self.totalTime,
                airmass, self.extinction)
        lowLim = 8E-5
        upLim = 9E-5
        self.assertGreater(result, lowLim)
        self.assertLess(result, upLim)

        mag = 12.
        airmass = 1.

        result = sourceError(self.expTime, mag, self.zp, self.readTime, self.totalTime,
                airmass, self.extinction)
        lowLim = 3E-4
        upLim = 4E-4
        self.assertGreater(result, lowLim)
        self.assertLess(result, upLim)

        airmass = 2.

        result = sourceError(self.expTime, mag, self.zp, self.readTime, self.totalTime,
                airmass, self.extinction)
        lowLim = 3E-4
        upLim = 4E-4
        self.assertGreater(result, lowLim)
        self.assertLess(result, upLim)

    def test_scintillation_error(self):
        apsize = 0.2
        height = 2400.
        mag = 9.

        airmass = 1.
        result = scintillationError(mag, self.zp, apsize, self.readTime, airmass, 
                self.extinction, height, self.expTime, self.totalTime,
                apsize)

        lowLim = 1E-4
        upLim = 2E-4
        self.assertGreater(result, lowLim)
        self.assertLess(result, upLim)

        airmass = 2.
        result = scintillationError(mag, self.zp, apsize, self.readTime, airmass, 
                self.extinction, height, self.expTime, self.totalTime,
                apsize)

        lowLim = 3E-4
        upLim = 4E-4
        self.assertGreater(result, lowLim)
        self.assertLess(result, upLim)

        mag = 12.

        airmass = 1.
        result = scintillationError(mag, self.zp, apsize, self.readTime, airmass, 
                self.extinction, height, self.expTime, self.totalTime,
                apsize)

        lowLim = 9E-5
        upLim = 2E-4
        self.assertGreater(result, lowLim)
        self.assertLess(result, upLim)

        airmass = 2.
        result = scintillationError(mag, self.zp, apsize, self.readTime, airmass, 
                self.extinction, height, self.expTime, self.totalTime,
                apsize)

        lowLim = 3E-4
        upLim = 4E-4
        self.assertGreater(result, lowLim)
        self.assertLess(result, upLim)

    def test_readnoise(self):
        readNoise = 11.7
        npix = 1.5**4 * np.pi
        mag = 9.
        airmass = 1.
        result = readError(mag, self.zp, self.readTime, readNoise, npix, 100., self.totalTime,
                self.extinction, airmass)

        lowLim = 1.5E-6
        upLim = 3E-6
        self.assertGreater(result, lowLim)
        self.assertLess(result, upLim)


        airmass = 2.
        result = readError(mag, self.zp, self.readTime, readNoise, npix, 100., self.totalTime,
                self.extinction, airmass)

        lowLim = 1.5E-6
        upLim = 3E-6
        self.assertGreater(result, lowLim)
        self.assertLess(result, upLim)

        mag = 12.
        airmass = 1.
        result = readError(mag, self.zp, self.readTime, readNoise, npix, 100., self.totalTime,
                self.extinction, airmass)

        lowLim = 3E-5
        upLim = 4E-5
        self.assertGreater(result, lowLim)
        self.assertLess(result, upLim)


        airmass = 2.
        result = readError(mag, self.zp, self.readTime, readNoise, npix, 100., self.totalTime,
                self.extinction, airmass)

        lowLim = 3E-5
        upLim = 4E-5
        self.assertGreater(result, lowLim)
        self.assertLess(result, upLim)

    def test_skyerror(self):
        skypersec = 50.
        npix = 1.5**4 * np.pi

        mag = 9.
        airmass = 1.
        result = skyError(mag, self.zp, self.readTime, skypersec, npix, self.expTime, self.totalTime, airmass, self.extinction)
        lowLim = 1E-5
        upLim = 2E-5
        self.assertGreater(result, lowLim)
        self.assertLess(result, upLim)

        airmass = 2.
        result = skyError(mag, self.zp, self.readTime, skypersec, npix, self.expTime, self.totalTime, airmass, self.extinction)
        lowLim = 1E-5
        upLim = 2E-5
        self.assertGreater(result, lowLim)
        self.assertLess(result, upLim)


        mag = 12.
        airmass = 1.
        result = skyError(mag, self.zp, self.readTime, skypersec, npix, self.expTime, self.totalTime, airmass, self.extinction)
        lowLim = 1E-4
        upLim = 2E-4
        self.assertGreater(result, lowLim)
        self.assertLess(result, upLim)

        airmass = 2.
        result = skyError(mag, self.zp, self.readTime, skypersec, npix, self.expTime, self.totalTime, airmass, self.extinction)
        lowLim = 1E-4
        upLim = 2E-4
        self.assertGreater(result, lowLim)
        self.assertLess(result, upLim)


if __name__ == '__main__':
    unittest2.main()

