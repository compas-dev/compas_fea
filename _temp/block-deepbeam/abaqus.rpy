# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 6.14-1 replay file
# Internal Version: 2014_06_05-00.11.02 134264
# Run by al on Mon Sep 25 18:20:42 2017
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(1.18555, 1.19792), width=174.512, 
    height=118.833)
session.viewports['Viewport: 1'].makeCurrent()
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
execfile('C:/Users/al/Dropbox/compas_fea/src/compas_fea/fea/abaq/odb.py', 
    __main__.__dict__)
#: Model: C:/Temp/block-deepbeam/block-deepbeam.odb
#: Number of Assemblies:         1
#: Number of Assembly instances: 0
#: Number of Part instances:     1
#: Number of Meshes:             1
#: Number of Element Sets:       3
#: Number of Node Sets:          4
#: Number of Steps:              1
print 'RT script done'
#: RT script done
