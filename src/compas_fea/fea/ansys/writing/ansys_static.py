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
    filename += '.txt'
    ansys_open_pre_process(output_path, filename)
    write_all_materials(structure, output_path, filename)
    write_nodes(structure, output_path, filename)
    write_elements(structure, output_path, filename)
    loads = []
    for skey in structure.steps_order:
        displacements = structure.steps[skey].displacements
        factor = structure.steps[skey].factor
        loads.extend(structure.steps[skey].loads)
        write_static_solve(structure, output_path, filename, skey)
        write_constraint_nodes(structure, output_path, filename, displacements)
        write_loads(structure, output_path, filename, loads, factor)
        write_request_load_step_file(structure, output_path, filename)
    write_request_solve_steps(structure, output_path, filename)


def write_request_load_step_file(structure, output_path, filename):
    cFile = open(output_path + filename, 'a')
    cFile.write('! \n')
    cFile.write('LSWRITE ! \n')
    cFile.write('!\n')
    cFile.close()


def write_request_solve_steps(structure, output_path, filename):
    mstep = len(structure.steps_order)
    cFile = open(output_path + filename, 'a')
    cFile.write('! \n')
    cFile.write('LSSOLVE, 1,' + str(mstep) + ',1! \n')
    cFile.write('!\n')
    cFile.close()


def write_static_solve(structure, output_path, filename, skey):
    cFile = open(output_path + filename, 'a')
    cFile.write('! \n')
    cFile.write('/SOLU ! \n')
    cFile.write('ANTYPE,0\n')
    cFile.write('!\n')
    if structure.steps[skey].nlgeom:
        cFile.write('NLGEOM,ON\n')  # add automatic time steps and max substeps/increments
        cFile.write('NSUBST,20,1000,1\n')
        cFile.write('AUTOTS,1\n')
        cFile.write('!\n')
    cFile.close()


def write_request_static_results(output_path, filename, step_name, fields):
    write_request_node_displacements(output_path, filename, step_name)
    write_request_nodal_stresses(output_path, filename, step_name)
    write_request_pricipal_stresses(output_path, filename, step_name)
    write_request_shear_stresses(output_path, filename, step_name)
    write_request_principal_strains(output_path, filename, step_name)
    write_request_reactions(output_path, filename, step_name)


def write_static_results_from_ansys_rst(name, path, fields, step_index=0, step_name='step'):

    if type(fields) == str:
        fields = [fields]
    if 'U' in fields or 'all' in fields:
        write_request_node_displacements(path, name, step_name)
    if 'S' in fields or 'all' in fields:
        write_request_nodal_stresses(path, name, step_name)
    if 'SP' in fields or 'all' in fields:
        write_request_pricipal_stresses(path, name, step_name)
    if 'SS' in fields or 'all' in fields:
        write_request_shear_stresses(path, name, step_name)
    if 'E' in fields or 'all' in fields:
        write_request_principal_strains(path, name, step_name)
    if 'R' in fields or 'all' in fields:
        write_request_reactions(path, name, step_name)


