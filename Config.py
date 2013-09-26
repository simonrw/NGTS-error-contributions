# -*- coding: utf-8 -*-

'''
This file contains the initial assumptions
passed throughout the analysis
'''
import logging
from numpy import pi
from AstErrors import NGTSDetector

logging.basicConfig(level=logging.INFO)

_detector = NGTSDetector()

Gain = 2.1
HorizontalSpeed = _detector.horizspeed
VerticalTime = _detector.verttime
NAXIS1, NAXIS2 = _detector.ccdsize
ReadTime = _detector.readTime()
ReadNoise = 15. # e- per pix
FWHM = 1.0
Radius = 1.5 * FWHM # pixels
Area = pi * Radius**2
BiasLevelADU = 1667 # ADU
BiasLevel = BiasLevelADU * Gain
Digitisation = 16
ElectronicSatur = ((2**Digitisation - 1)) * Area
TargetBinTime = 3600.
FullWellDepth = 107E3
FieldCentre = [(60., -45.), (180., -45.), (300., -45.)]
PixScale = 4.97
SkyLevel = {
        'dark': 50.,
        'bright': 450.,
        }
