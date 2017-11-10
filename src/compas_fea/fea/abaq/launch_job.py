"""
Launch an Abaqus job.
"""

try:
    from abaqus import *
    from abaqusConstants import *
except:
    pass

import sys


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


if __name__ == "__main__":

    name = sys.argv[-1]
    path = sys.argv[-2]
    cpus = int(sys.argv[-3])

    inp = '{0}{1}.inp'.format(path, name)
    job = mdb.JobFromInputFile(name=name, inputFileName=inp, numCpus=cpus, numDomains=cpus,
                               multiprocessingMode=DEFAULT, parallelizationMethodExplicit=DOMAIN)
    job.submit()
    job.waitForCompletion()
