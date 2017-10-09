from compas_fea.fea.ansys.writing.ansys_nodes_elements import *
from compas_fea.fea.ansys.writing.ansys_stresses import *
from compas_fea.fea.ansys.writing.ansys_materials import *
from compas_fea.fea.ansys.writing.ansys_loads import *
from compas_fea.fea.ansys.writing.ansys_process import *

__author__     = ['Tomas Mendez Echenagucia <mendez@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'mendez@arch.ethz.ch'


def write_static_analysis_request(structure, output_path, filename):
    write_preprocess(output_path, filename)
    write_all_materials(structure, output_path, filename)
    write_nodes(structure, output_path, filename)
    write_elements(structure, output_path, filename)
    for skey in structure.steps['order']:
        displacements = structure.steps[skey].displacements
        factor = structure.steps[skey].factor
        loads = structure.steps[skey].loads
        write_constraint_nodes(structure, output_path, filename, displacements)
        write_loads(structure, output_path, filename, loads, factor)
        write_static_solve(structure, output_path, filename, skey)
        step_path = output_path + 'out/' + str(skey + '/')
        if not os.path.exists(step_path):
            os.makedirs(step_path)
        write_request_static_results(structure, step_path, filename, skey)


def write_static_solve(structure, output_path, filename, skey):
    cFile = open(output_path + filename, 'a')
    cFile.write('! \n')
    # cFile.write('TIME,'+skey+'!\n')
    cFile.write('/SOL ! \n')
    cFile.write('ANTYPE,0\n')
    cFile.write('!\n')
    if structure.steps[skey].nlgeom:
        cFile.write('ANTYPE,0\n')
        cFile.write('NLGEOM,ON\n')
        cFile.write('NSUBST,20,1000,1\n')
        cFile.write('AUTOTS,1\n')
        cFile.write('!\n')


def write_request_static_results(structure, output_path, filename, skey):
    write_post_process(output_path, filename)
    write_request_element_nodes(output_path, filename)
    write_request_node_displacements(output_path, filename)
    write_request_nodal_stresses(output_path, filename)
    write_request_pricipal_stresses(output_path, filename)
    write_request_shear_stresses(output_path, filename)
    write_request_principal_strains(output_path, filename)
    write_request_reactions(output_path, filename)
