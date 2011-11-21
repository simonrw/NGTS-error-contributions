from ppgplot import *
from numpy import *



class PlotClass(object):
    _reqKeys = ['xdata', 'ydata', 'label',
            'colour', 'ls']

    class PlotClassError(Exception):
        "Exception class"

    def __init__(self, device):
        super(PlotClass, self).__init__()
        self._lines = []
        self._extraLines = []
        self._device = device
        self._xmin = None
        self._xmax = None
        self._ymin = None
        self._ymax = None
        self._log = True
        self._extra = 0.05

        self._labels = {'x': "", "y": "", "title": ""}

        # legend variables
        self._legendxmin = 0.7
        self._linelength = 0.03
        self._legendymin = 0.1
        self._inc = 0.04
        self._spacing = 0.01

        pgopen(self._device)

    def log(self, boolval):
        self._log = boolval

    def _validateLine(self, line):
        valid = True
        linekeys = line.keys()
        for key in self._reqKeys:
            valid &= (key in linekeys)

        return valid


    def __del__(self):
        pgclos()

    def xrange(self, xmin, xmax):
        if xmin:
            self._xmin = xmin
        if xmax: 
            self._xmax = xmax

    def yrange(self, ymin, ymax):
        if ymin:
            self._ymin = ymin
        if ymax: 
            self._ymax = ymax
        
    def addLine(self, line):
        '''
        Line must be a dictionary with the following keys:
            * xdata
            * ydata 
            * label
            * colour
            * ls
        '''
        if self._validateLine(line):
            self._lines.append(line)
        else:
            raise self.PlotClassError("Invalid line format")

    def line(self, point, direction, ls=2, colour=1):
        if direction == 'x':
            self._extraLines.append({
                'ydata': array([point, point]),
                'colour': colour,
                'ls': ls,
                'legend': False,
                })
        elif direction == 'y':
            self._extraLines.append({
                'xdata': array([point, point]),
                'colour': colour,
                'ls': ls,
                'legend': False,
                })


    def _setLimits(self):
        if self._log:
            minx = min([log10(a['xdata'].min()) for a in self._lines]) - self._extra
            maxx = max([log10(a['xdata'].max()) for a in self._lines]) + self._extra
            miny = min([log10(a['ydata'].min()) for a in self._lines]) - self._extra
            maxy = max([log10(a['ydata'].max()) for a in self._lines]) + self._extra

            if self._xmin: minx = self._xmin
            if self._xmax: maxx = self._xmax
            if self._ymin: miny = self._ymin
            if self._ymax: mayx = self._ymax

            pgenv(minx, maxx, miny, maxy, 0, 30)

            self._xmin = minx
            self._xmax = maxx
            self._ymin = miny
            self._ymax = mayx



        else:
            minx = min([a['xdata'].min() for a in self._lines]) * (1-self._extra)
            maxx = max([a['xdata'].max() for a in self._lines]) * (1+self._extra)
            miny = min([a['ydata'].min() for a in self._lines]) * (1-self._extra)
            maxy = max([a['ydata'].max() for a in self._lines]) * (1+self._extra)

            if self._xmin: minx = self._xmin
            if self._xmax: maxx = self._xmax
            if self._ymin: miny = self._ymin
            if self._ymax: mayx = self._ymax


            pgenv(minx, maxx, miny, maxy, 0, 0)

            self._xmin = minx
            self._xmax = maxx
            self._ymin = miny
            self._ymax = mayx

        xdiff = self._xmax - self._xmin
        self._legendxmin = self._legendxmin * (self._xmax - self._xmin) + self._xmin
        self._legendymin = self._legendymin * (self._ymax - self._ymin) + self._ymin
        self._inc *= xdiff
        self._linelength *= xdiff
        self._spacing *= xdiff


    def _plotLine(self, line, i=0):
        if self._log:
            xdata = log10(line['xdata'])
            ydata = log10(line['ydata'])
        else:
            xdata = line['xdata']
            ydata = line['ydata']

        pgsls(line['ls'])
        pgsci(line['colour'])
        pgline(xdata, ydata)

        if line['legend']:
            # Only do this if the line has a label parameter
            try:
                label = line['label']
            except KeyError:
                pgsci(1)
                pgsls(1)
            else:
                # plot the legend
                xval = self._legendxmin + self._linelength + self._spacing
                yval = self._legendymin + i * self._inc
                pgsls(line['ls'])
                pgsci(line['colour'])
                pgline(array([self._legendxmin, self._legendxmin+self._linelength]),
                        array([self._legendymin + i * self._inc, self._legendymin + i * self._inc])
                        )
                pgsci(1)
                pgsls(1)
                pgtext(xval, yval, line['label'])

    def title(self, title):
        self._labels['title'] = title

    def xlabel(self, xlabel):
        self._labels['x'] = xlabel

    def ylabel(self, ylabel):
        self._labels['y'] = ylabel

    def setLabels(self, xlabel, ylabel, title):
        self.xlabel(xlabel)
        self.ylabel(ylabel)
        self.title(title)

    def _renderlabels(self):
        pglab(self._labels['x'],
                self._labels['y'],
                self._labels['title'])



    def render(self):
        if not len(self._lines):
            raise self.PlotClassError("No lines added")

        # Get the line limits
        self._setLimits()




        # plot all of the lines
        for i, line in enumerate(self._lines):
            self._plotLine(line, i)




        # add the extra lines to the lines array
        for line in self._extraLines:
            # assume it's a vertical line
            try:
                xpoint = line['xdata'][0]
            except KeyError:
                ypoint = line['ydata'][0]
                xdata = array([self._xmin, self._xmax])
                if self._log:
                    xdata = 10**xdata
                line['xdata'] = xdata
            else:
                ydata = array([self._ymin, self._ymax])
                if self._log:
                    ydata = 10**ydata
                line['ydata'] = ydata
            finally:
                self._plotLine(line)

        self._renderlabels()


def Plot(device, lines, colours, saturlevel, log=True, characterScale=1.0,
        lineWidth=1, ymin=None, ymax=None, title=None):
    r'''
    Plotting function

    Takes parameters:
        * Plot device
        * Container of line objects (x, y, label)
        * Container of colours
        * Saturation level (in x)
        * Logarithm flag
        * Character scale (makes text larger)
        * Line width (makes lines thicker)
        * ymin/ymax - manual plot y limits
        * Title of the plot
    '''

    assert len(lines) <= len(colours)
    pgopen(device)
    origCharHeight = pgqch()
    pgsch(characterScale)

    extra = 0.05
    legendCoords = (0.1, 0.1)



    # get the limits 
    if log:
        minx = min([log10(a[0].min()) for a in lines]) - extra
        maxx = max([log10(a[0].max()) for a in lines]) + extra
        miny = min([log10(a[1].min()) for a in lines]) - extra
        maxy = max([log10(a[1].max()) for a in lines]) + extra

        SaturationLevel = log10(saturlevel)
        

        if ymin and not ymax:
            miny = ymin
        elif ymax and not ymin:
            maxy = ymax
        elif not ymin and not ymax:
            pass
        else:
            miny = ymin
            maxy = ymax

        pgenv(minx, maxx, miny, maxy, 0, 30)
    else:
        minx = min([a[0].min() for a in lines]) * (1-extra)
        maxx = max([a[0].max() for a in lines]) * (1+extra)
        miny = min([a[1].min() for a in lines]) * (1-extra)
        maxy = max([a[1].max() for a in lines]) * (1+extra)

        SaturationLevel = saturlevel

        if ymin and not ymax:
            miny = ymin
        elif ymax and not ymin:
            maxy = ymax
        elif not ymin and not ymax:
            pass
        else:
            miny = ymin
            maxy = ymax

        pgenv(minx, maxx, miny, maxy, 0, 30)


    legendxmin = legendCoords[0] * (maxx - minx) + minx
    legendymin = legendCoords[1] * (maxy - miny) + miny
    inc = 0.04 * (maxx - minx)
    linelength = 0.03 * (maxx - minx)
    spacing = 0.01 * (maxx - minx)


    origLineWidth = pgqlw()


    for i, lc in enumerate(lines):
        colour = colours[i]
        x = lc[0]
        y = lc[1]
        label = lc[2]

        pgslw(lineWidth)
        pgsci(colour)
        if log:
            pgline(log10(x), log10(y))
        else:
            pgline(x, y)

        pgline(array([legendxmin, legendxmin+linelength]),
                array([legendymin + i * inc, legendymin + i * inc])
                )

        pgslw(origLineWidth)

        pgsci(1)
        pgtext(legendxmin + linelength + spacing, legendymin + i * inc, label)


    # Plot the saturation level
    pgsls(2)
    pgslw(lineWidth)
    pgline(array([SaturationLevel, SaturationLevel]), array([miny, maxy]))
    pgslw(origLineWidth)
    pgsls(1)

    if not title:
        pglab(r'Exposure time per frame / s', r'Fractional error after binning to an hour', '')
    else:
        pglab(r'Exposure time per frame / s', r'Fractional error after binning to an hour', title)



    pgclos()

