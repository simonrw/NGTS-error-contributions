from numpy import *

class PlotClass(object):
    _reqKeys = ['xdata', 'ydata', 'label',
            'colour', 'ls']

    class PlotClassError(Exception):
        "Exception class"

    def __init__(self):
        super(PlotClass, self).__init__()


    def log(self, boolval):
        self._log = boolval

    def _validateLine(self, line):
        valid = True
        linekeys = list(line.keys())
        for key in self._reqKeys:
            valid &= (key in linekeys)

        return valid

    def addLine(self, line):
        pass

    def line(self, point, direction, ls=2, colour=1):
        pass

    def _plotLine(self, line, i=0):
        pass


    def title(self, title):
        pass


    def xlabel(self, xlabel):
        pass


    def ylabel(self, ylabel):
        pass


    def setLabels(self, xlabel, ylabel, title):
        pass


    def render(self):
        pass

    def xrange(self, xmin, xmax):
        pass

    def yrange(self, ymin, ymax):
        pass


