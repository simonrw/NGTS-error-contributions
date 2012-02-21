#!/usr/bin/env python
# encoding: utf-8

'''
This script updates all of the data for each data set 
given the config file Config.py.

The output of all of the scripts can be plotted to a directory 
given on the command line with the -o argument
'''

import subprocess as sp
import hashlib
import argparse
import os.path
import os
import shutil

BASEDIR = os.path.dirname(__file__)

def generate_hash(filepath):
    try:
        with open(filepath, 'rb') as f:
            return hashlib.sha224(f.read()).hexdigest()
    except IOError:
        # File does not exist
        return 0

def mkdir(path):
    try:
        os.makedirs(path)
    except OSError:
        # Directory already exists
        shutil.rmtree(path)
        os.makedirs(path)

def logfilename(path, scriptname, type='out'):
    '''
    Constructs a logfile name
    '''
    stub = os.path.splitext(scriptname)[0]
    logname = stub + ".log"
    if type.lower() == "out":
        logname += ".out"
    elif type.lower() == "err":
        logname += ".err"
    else:
        raise RuntimeError("Cannot determine log type, must be 'out' or 'err'")

    logoutname = os.path.join(
            path,
            os.path.basename(logname)
            )


    return logoutname



class App(object):
    """Main application"""

    '''
    List of scripts and their arguments
    '''

    exptime = 5
    targetmag = 9


    def __init__(self, args):
        """@todo: to be defined
        
        @param args @todo
        """
        self._args = args

        # If output argument given, generate the plots 
        if self._args.output:
            self.plotData()
        else:
            self.updateFits()

    def updateFits(self):
        hash_before = generate_hash("fits.cpickle")

        # Update the saturation vs exposure plot
        scriptname = os.path.join(BASEDIR,
                "SaturationVsExposure.py")

        print "Generating saturation trend"
        sp.call([scriptname, "-d", "null"], stderr=sp.PIPE, 
            stdout=sp.PIPE)

        if generate_hash("fits.cpickle") == hash_before:
            print "Fits have not been updated"
        else:
            print "Fits updated"



    def plotData(self):
        # First create the output directory
        mkdir(self._args.output)
        logpath = os.path.join(self._args.output, "logs")
        mkdir(logpath)

        i = 1


        self.scripts = [
                {'bin': os.path.join(BASEDIR, "SaturationVsExposure.py"),
                    'args': ["-d", os.path.join(self._args.output, "SaturationVsExposure.ps/cps")],
                        },
                    {'bin': os.path.join(BASEDIR, 'ErrorContributions.py'),
                        'args': ["-m", "9", "-d",
                            os.path.join(self._args.output, "ErrorContributions_bright.ps/cps")],
                        },
                    {'bin': os.path.join(BASEDIR, 'ErrorContributions.py'),
                        'args': ["-m", "15", "-d",
                            os.path.join(self._args.output, "ErrorContributions_faint.ps/cps")],
                        },
                    {'bin': os.path.join(BASEDIR, 'TheoryNoiseWithBinning.py'),
                        'args': ["-e", "5", "-d", 
                            os.path.join(self._args.output, "TheoryNoiseWithBinning_5s.ps/cps")],
                        },
                    {'bin': os.path.join(BASEDIR, 'TheoryNoiseWithBinning.py'),
                        'args': ["-e", "30", "-d", 
                            os.path.join(self._args.output, "TheoryNoiseWithBinning_30s.ps/cps")],
                        },
                    {'bin': os.path.join(BASEDIR, 'NSaturatedInField.py'),
                        'args': ["-d",
                            os.path.join(self._args.output, "NSaturatedInField.ps/cps")],
                        },
                    {'bin': os.path.join(BASEDIR, 'NumberOfExposures.py'),
                        'args': ["5"],
                        },
                    {'bin': os.path.join(BASEDIR, 'NumberOfExposures.py'),
                        'args': ["30"],
                        },
                    ]
        
        for s in self.scripts:
            key = s['bin']
            value = s['args']
            print "Calling %s" % key
            cmd = [key]
            cmd.extend(value)

            logoutname = logfilename(logpath, key, type='out')
            logerrname = logfilename(logpath, key, type='err')

            if os.path.isfile(logoutname) and os.path.isfile(logerrname):
                logoutname += ".%d" % i
                logerrname += ".%d" % i

                i += 1



            #print cmd
            sp.call(cmd, stdout=open(logoutname, 'w'), stderr=open(logerrname, 'w'))



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="Directory to put plots",
            required=False, default=None, type=str)
    args = parser.parse_args()
    app = App(args)
