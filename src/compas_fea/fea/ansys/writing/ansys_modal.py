from .ansys_nodes_elements import write_request_element_nodes
from .ansys_nodes_elements import write_request_node_displacements
from .ansys_nodes_elements import write_constraint_nodes
from .ansys_nodes_elements import write_nodes
from .ansys_nodes_elements import write_elements
from .ansys_materials import write_all_materials
from compas_fea.fea.ansys.writing.ansys_process import *

__author__     = ['Tomas Mendez Echenagucia <mendez@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'mendez@arch.ethz.ch'


def write_modal_analysis_request(structure, output_path, filename, skey):
    displacements = structure.steps[skey].displacements
    ansys_open_post_process(output_path, filename)
    write_all_materials(structure, output_path, filename)
    write_nodes(structure, output_path, filename)
    write_elements(structure, output_path, filename)
    write_constraint_nodes(structure, output_path, filename, displacements)
    write_modal_solve(structure, output_path, filename, skey)
    write_modal_post_process(output_path, filename)
    write_request_element_nodes(output_path, filename)
    write_request_modal_freq(structure, output_path, filename, skey)
    write_request_modal_shapes(structure, output_path, filename, skey)


def write_modal_solve(structure, output_path, filename, skey):
    num_modes = structure.steps[skey].modes
    cFile = open(output_path + "/" + filename, 'a')
    cFile.write('/SOL \n')
    cFile.write('!\n')
    cFile.write('ANTYPE,2 \n')
    cFile.write('MODOPT,SUBSP,' + str(num_modes) + '\n')
    cFile.write('EQSLV,FRONT \n')
    cFile.write('MXPAND,' + str(num_modes) + ',,,YES \n')

    # if structure.geom_nonlinearity is True:
    #     cFile.close()
    #     write_geom_nonlinearity(output_path, filename)
    #     cFile = open(output_path + "/" + filename, 'a')

    cFile.write('SOLVE')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_modal_post_process(output_path, filename):
    cFile = open(output_path + "/" + filename, 'a')
    cFile.write('/POST1 \n')
    cFile.write('SET,FIRST \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_request_modal_freq(structure, output_path, filename, skey):
    num_modes = structure.steps[skey].modes
    cFile = open(output_path + "/" + filename, 'a')
    cFile.write('/SOL \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.write('*set,n_freq, \n')
    cFile.write('*dim,n_freq,array,' + str(num_modes) + ', \n')

    for i in range(num_modes):
        cFile.write('*GET,n_freq(' + str(i + 1) + '),MODE,' + str(i + 1) + ',FREQ \n')

    cFile.write('*dim,nds,,' + str(num_modes) + ',1 \n')
    cFile.write('*vfill,nds(1),ramp,1,1 \n')
    cFile.write('*cfopen,' + output_path + 'modal_out/modal_freq,txt \n')
    cFile.write('*vwrite, nds(1) , \',\'  , n_freq(1) \n')
    cFile.write('(          F8.0,       A,       ES) \n')
    cFile.write('*cfclose \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_request_modal_shapes(structure, output_path, filename, skey):
    num_modes = structure.steps[skey].modes
    cFile = open(output_path + "/" + filename, 'a')
    cFile.write('/POST1 \n')
    cFile.close()
    for i in range(num_modes):
        cFile = open(output_path + "/" + filename, 'a')
        cFile.write('SET,NEXT \n')
        cFile.write('! Mode ' + str(i + 1) + ' \n \n \n')
        cFile.close()
        write_request_node_displacements(output_path, filename, mode=i + 1)
