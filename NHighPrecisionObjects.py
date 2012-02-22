#!/usr/bin/env python
# encoding: utf-8

from Config import *
import cPickle
import numpy as np
from scipy.interpolate import interp1d
from srw.NOMADParser import NOMADParser
import matplotlib.pyplot as plt
import BesanconParser

from jg.subs import progressbarClass

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

def highPrecision(mag, t):
    '''
    Returns if the object has a high precision
    '''
    currentRange = rangeAtExptime(t)
    returnval = False
    if (mag > currentRange[0]) & (mag <= currentRange[1]):
        returnval = True


    return returnval

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




    def fetch(self):
        field = self.fields[self.currentField]
        self.parser = NOMADParser(field[0], field[1], 60.)
        #self.data = filter(None, [result['vmag'] for result in self.parser.fetch()])
        self.data = np.array(filter(None, [result['vmag'] for result in self.parser.fetch()]))



        
    

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

            #data[parser['name']][field] = [parser['parser'].percentage(e) for e in exptimes]
            profileAx.plot(exptimes, [parser['parser'].percentage(e) for e in exptimes], label="NOMAD %d" % field)

                

        parser['parser'].close()

        #data[parser['name']] = fractionHist


    #for field in fields:
        #profileAx.plot(exptimes, data['NOMAD'][field], ls='-', label='NOMAD %d' % field)
    #profileAx.plot(exptimes, data['Besancon'], 'r-', label='Besancon')

    profileAx.legend(loc='best')
    #print "Saving figure as NHighPrecision.pdf"
    profileAx.set_xlabel("Exposure time / s")
    profileAx.set_ylabel("Percentage of high precision stars / %")
    #plt.savefig("NHighPrecision.pdf")

    #histAllAx = fig.add_subplot(212)
    ##histAllAx.hist([visibleMags[k] for k in visibleMags], 50,
            ##label=visibleMags.keys(), log=True)
    #histAllAx.hist(visibleMags['NOMAD'], 50, label="NOMAD", fc='0.7')
    #histAllAx.set_xlabel("I magnitude")
    #histAllAx.legend(loc='best')
    plt.show()



#xpoints = np.linspace(5, 50, 100)
#pb = progressbarClass(xpoints.size * len(FieldCentre))
#counter = 1
#fieldcounter = 1
#for fc in FieldCentre:
    #parser = NOMADParser(fc[0], fc[1], 60.)
    #results = parser.fetch()


    #vmags = filter(lambda mag: mag != None, [result['vmag'] for result in results])

    #nVisible = len(filter(lambda mag: mag < 17, vmags))
    
    #nTotal = len(vmags)

    ##print "Field:", fc, " total: %d, visible: %d" % (nTotal, nVisible)
    #fraction = []
    #for e in xpoints:
        #nSelected = len(filter(lambda mag: highPrecision(mag, e), vmags))
        #fraction.append(nSelected * 100. / float(nVisible))
        ##print "%.2fs = %d / %d = %f%%" % (e, nSelected, nVisible, float(nSelected) * 100./ nVisible)
        #pb.progress(counter)

        #counter += 1


    #plt.plot(xpoints, fraction, label="Field (%d, %d)" % (fc[0], fc[1]))

#plt.xlabel("Exposure time / s")
#plt.ylabel("Percentage of high precision stars / %")

#plt.legend(loc='best')
#plt.show()


