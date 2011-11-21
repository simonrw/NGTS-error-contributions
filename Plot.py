from ppgplot import *
from numpy import *

class PlotClass(object):
    def __init__(self):
        super(PlotClass, self).__init__()
        self._lines = []

        
    def addLine(self, line):
        self.lines.append(line)


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

