'''
This file contains the initial assumptions
passed throughout the analysis
'''
from numpy import pi
from AstErrors import WASPDetector

_detector = WASPDetector()

Gain = 2.71
HorizontalSpeed = _detector.horizspeed
VerticalTime = _detector.verttime
NAXIS1, NAXIS2 = _detector.ccdsize
ReadTime = _detector.readTime()
ReadNoise = 3.36 # e- per pix
FWHM = 1.5
#Radius = 1.5 * FWHM # pixels
Radius = 2.5
Area = pi * Radius**2
BiasLevelADU = 1042 # ADU
BiasLevel = BiasLevelADU * Gain
Digitisation = 16
ElectronicSatur = ((2**Digitisation - 1)) * Area
TargetBinTime = 3600.
FullWellDepth = 80E3
FieldCentre = [(60., -45.), (180., -45.), (300., -45.)]
PixScale = 13.7
