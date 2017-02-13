#!/usr/bin/env python

import json
import numpy as np


class Fits(object):

    def __init__(self):
        self.dark_fit = np.poly1d([-0.24445729,  3.48611203,  6.34602232])
        self.bright_fit = np.poly1d([-4.7810172,  27.96839962, -56.36501281,
                                     50.95593997,  -7.84970971])
        self._mapping = {
            'dark': self.dark_fit,
            'bright': self.bright_fit,
        }

    def __getitem__(self, name):
        return self._mapping[name]
