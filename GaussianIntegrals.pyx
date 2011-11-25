from libc.math cimport exp
import numpy as np

cdef float a2dGaussian(float y, float x, float fwhm):
    cdef float sigma, arg1, arg2, exponent
    sigma = fwhm / 2.35

    arg1 = x**2 / sigma**2
    arg2 = y**2 / sigma**2
    exponent = -0.5 * (arg1 + arg2)
    return exp(exponent)

def Py2dGaussian(y, x, fwhm):
    return a2dGaussian(y, x, fwhm)


cdef float Integrate(float fwhm, float dx, float dy, float low, float high):
    cdef float dA, sumval, y, x
    dA = dx * dy
    sumval = 0.
    for y in np.arange(low, high, dy):
        for x in np.arange(low, high, dx):
            sumval += Py2dGaussian(y, x, fwhm) * dA

    return sumval

def PyIntegrate(fwhm, dx, dy, low, high):
    return Integrate(fwhm, dx, dy, low, high)


def PyDistribution(fwhm, dx, offset):
    pass
