#!/usr/bin/env python
# encoding: utf-8

'''
How many stars are within the high precision
range (with precision of <1mmag and not saturated)
for varying exposure times, using both the
Besancon model and real field data
'''

import subprocess as sp
import os.path
import matplotlib.pyplot as plt
import numpy as np
import multiprocessing
import argparse

import cPickle

dataScriptName = os.path.join(
        os.path.dirname(__file__),
        "TheoryNoiseWithBinning.py"
        )

def getStatsForExptime(time):
    '''
    Calls the script which provides the data,
    and parses the results
    '''
    print "T: %.1f" % time
    cmd = [dataScriptName, "-o", "/tmp/output.png", "-e", str(time), "-v"]
    p = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
    linestr, err = p.communicate()
    lines = linestr.split("\n")
    crosspoint = float(filter(lambda line: "CROSSPOINT" in line, lines)[0].split()[-1])
    satpoint = float(filter(lambda line: "DARK" in line, lines)[0].split()[-1])
    return crosspoint, satpoint

class App(object):
    """Main application"""

    # Script to run which provides the
    # limits data

    # list of exposure times
    _exptimes = 10 ** np.linspace(np.log10(1), np.log10(50), 20)
    #_exptimes = [1, 5, 10]

    def __init__(self, args):
        """@todo: to be defined

        @param args @todo
        """

        answer = raw_input("This program generates the data. It takes a while. "
                "Are you sure you want to run this, and not just plot the data using "
                "PlotHighPrecisionRange.py? [y/N] ")

        if answer.upper() != "Y":
            print "Exiting"
            exit()


        self._args = args
        self.fig = plt.figure(figsize=(11, 8))
        self.ax = self.fig.add_subplot(111)

        self.pool = multiprocessing.Pool()




    def run(self):
        crosspoints, satpoints = zip(*self.pool.map(getStatsForExptime, self._exptimes))

        self._exptimes = np.array(self._exptimes)
        self.crosspoints = np.array(crosspoints)
        self.satpoints = np.array(satpoints)

        self.dumpData()




    def dumpData(self):
        '''
        Dump the data to a cpickle file
        '''
        cPickle.dump(np.array([self._exptimes, self.crosspoints, self.satpoints]),
                open("precisiondata.cpickle", "w"),
                protocol=2)








if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="Save the figure",
            type=str, default=None, required=False)
    args = parser.parse_args()
    app = App(args)
    app.run()
