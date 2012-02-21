import matplotlib.pyplot as plt
import numpy as np
from Plot import PlotClass

class PylabPlotClass(PlotClass):

    def __init__(self, output=None, figsize=(11, 8)):
        self._lines = []
        self._output = output
        self._fig = plt.figure(figsize=figsize)
        self._ax = self._fig.add_subplot(111)
        self._log = True

    def __del__(self):
        '''
        Show the plot window 
        '''
        if self._log:
            self._ax.set_xscale("log")
            self._ax.set_yscale("log")

        if self._output:
            plt.savefig(self._output)
        else:
            plt.show()

    def addLine(self, line):
        self._validateLine(line)

        self._ax.plot(line['xdata'], line['ydata'], 
                label=line['label'])





