try:
    from abaqus import mdb
    from abaqusConstants import THREADS, DOMAIN
except ImportError:
    pass

import sys

# Author(s): Andrew Liew (github.com/andrewliew)

if __name__ == "__main__":

    name = sys.argv[-1]
    path = sys.argv[-2]
    cpus = int(sys.argv[-3])
    inp = '{0}{1}.inp'.format(path, name)

    if cpus == 1:
        job = mdb.JobFromInputFile(name=name, inputFileName=inp)
    else:
        job = mdb.JobFromInputFile(name=name, inputFileName=inp, numCpus=cpus, numDomains=cpus,
                                   multiprocessingMode=THREADS, parallelizationMethodExplicit=DOMAIN)
    job.submit()
    job.waitForCompletion()
