#!/usr/bin/env python
# encoding: utf-8

from Config import *
import cPickle
import numpy as np
from scipy.interpolate import interp1d
#from srw.NOMADParser import NOMADParser
from NOMADFields import NOMADFieldsParser
import matplotlib.pyplot as plt
import BesanconParser


exptimes, crosspoints, satpoints = cPickle.load(open("precisiondata.cpickle"))

interpcross = interp1d(exptimes, crosspoints, kind='linear')
interpsat = interp1d(exptimes, satpoints, kind='linear')


def rangeAtExptime(t):
    '''
    Returns the range in which a target is observed
    at 1mmag for a given exposure time.

    Returns:
        * lowest magnitude
        * highest magnitude
    '''
    return float(interpsat(t)), float(interpcross(t))


class DataStore(object):
    """
    Holds the data and provides
    unified IO for it
    """


    def __init__(self):
        """@todo: to be defined """

        self.fields = {
                1: (60, -45),
                2: (12 * 15, -45),
                3: (20 * 15, -45),
                }

        self.data = None
        self.currentField = None



    def setField(self, field):
        self.currentField = field
        self.fetch()

    def visible(self):
        '''
        Returns the magnitudes of all of the visible
        mag < 17 objects
        '''
        return self.data[self.data < 17]

    def highPrecision(self, e):
        '''
        Returns all of the magnitudes of the 
        high precision objects
        '''
        hpRange = rangeAtExptime(e)
        return self.data[(self.data > hpRange[0]) & (self.data <= hpRange[1])]

    def nVisible(self):
        '''
        Returns the number of visible objects
        '''
        #return len(self.visible())
        return self.visible().size

    def nHighPrecision(self, e):
        '''
        Returns the number of high precision objects
        '''
        #return len(self.highPrecision(e))
        return self.highPrecision(e).size

    def percentage(self, t):
        return float(self.nHighPrecision(t)) * 100. / float(self.nVisible())

    def fetch(self):
        raise NotImplementedError()

    def close(self):
        pass
        

class NOMADDataStore(DataStore):
    """
    Data store for the NOMAD database
    """

    def __init__(self):
        """@todo: to be defined """
        
        super(NOMADDataStore, self).__init__()

        self.parser = NOMADFieldsParser()



    def fetch(self):
        self.data = self.parser.getTable("/fields", "field%d" % self.currentField).cols.vmagnitude[:]
        self.data = self.data[self.data != 0]



        
    

class BesanconDataStore(DataStore):
    """
    Data store for the Besancon database
    """

    def __init__(self, restr=None):
        """@todo: to be defined """
        
        super(BesanconDataStore, self).__init__()
        self.restr = restr

    def fetch(self):
        self.parser = BesanconParser.BesanconParser()

        node = self.parser.getTable("/fields", "field%d" % self.currentField)

        if self.restr:
            self.data = np.array([row['imagnitude'] for row in node.where(self.restr)])
        else:
            self.data = node.cols.imagnitude[:]


    def close(self):
        self.parser.close()
        


if __name__ == '__main__':
    exptimes = np.linspace(5, 90, 50)
    #exptimes = [5,]

    visibleMags = {}
    fields = [1, 2, 3]

    # Select only the main sequence objects
    ModelRestrictions = "((typ == 5) | (typ == 6) | (typ == 7)) & (cl == 5)"

    fig = plt.figure()
    profileAx = fig.add_subplot(111)
    
    for parser in [{'name': 'NOMAD', 'parser': NOMADDataStore()},]:
            #{'name': 'Besancon', 'parser': BesanconDataStore(ModelRestrictions)}]:
        print parser['name']
        for field in fields:
            print "\tField %d" % field
            parser['parser'].setField(field)

            visibleMags[parser['name']] = parser['parser'].visible()

            if parser['name'] == "NOMAD":
                ls = "-"
            elif parser['name'] == "Besancon":
                ls = "--"

            profileAx.plot(exptimes, [parser['parser'].percentage(e) for e in exptimes], label="%s %d" % (parser['name'], field),
                    ls=ls)

                

        parser['parser'].close()


    profileAx.legend(loc='best')
    profileAx.set_xlabel("Exposure time / s")
    profileAx.set_ylabel("Percentage of high precision stars / %")
    plt.show()


