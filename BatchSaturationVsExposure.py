#!/usr/bin/env python

import subprocess
import argparse
import numpy as np
import os.path
import re
import multiprocessing
import matplotlib.pyplot as plt



class App(object):
    def __init__(self, args):
        super(App, self).__init__()
        self.args = args

        self.MagRange = (8.25, 13, 0.25)


        self.run()

    def run(self):
        mags = np.arange(*self.MagRange)
        times = []
        for mag in mags:
            cmd = [os.path.join(os.path.dirname(__file__),
                                "ErrorContributions.py"),
                    '-m', str(mag), "-d", "/null",
                    ]

            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result, error = p.communicate()

            result = float(re.search(r"Saturation in (\d+\.*\d+) seconds", result).group(1))
            print "Mag: %.2f, time: %.2f" % (mag, result)
            times.append(result)


        plt.plot(times, mags, 'r-')
        plt.show()






if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    app = App(args)


