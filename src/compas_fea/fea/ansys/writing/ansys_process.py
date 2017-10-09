
from compas_fea.fea.ansys.writing.ansys_nodes_elements import *
from compas_fea.fea.ansys.writing.ansys_stresses import *
from compas_fea.fea.ansys.writing.ansys_materials import *
from compas_fea.fea.ansys.writing.ansys_loads import *


__author__     = ['Tomas Mendez Echenagucia <mendez@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'mendez@arch.ethz.ch'


def write_post_process(output_path, filename):
    cFile = open(output_path + filename, 'a')
    cFile.write('/POST1 \n')
    cFile.write('SET,LAST \n')
    cFile.write('RAPPND,1, \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


# def write_step(output_path, filename, skey, nlgeom):
#     cFile = open(output_path + filename, 'a')
#     cFile.write('! \n')
#     # cFile.write('TIME,'+skey+'!\n')
#     cFile.write('/SOL ! \n')
#     cFile.write('ANTYPE,0\n')
#     cFile.write('!\n')
#     if nlgeom:
#         cFile.write('ANTYPE,0\n')
#         cFile.write('NLGEOM,ON\n')
#         cFile.write('NSUBST,20,1000,1\n')
#         cFile.write('AUTOTS,1\n')
#         cFile.write('!\n')

#     cFile.write('SOLVE!\n')
#     # cFile.write('TIME,'+skey+'!\n')
#     cFile.write('!\n')
#     cFile.close()


def write_preprocess(output_path, filename):
    cFile = open(output_path + filename, 'w')
    cFile.write('! Ansys command file writen from rhino \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.write('/PREP7 \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()
