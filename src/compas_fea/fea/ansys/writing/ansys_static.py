from compas_fea.fea.ansys.writing.ansys_nodes_elements import *
from compas_fea.fea.ansys.writing.ansys_stresses import *
from compas_fea.fea.ansys.writing.ansys_materials import *
from compas_fea.fea.ansys.writing.ansys_loads import *
from compas_fea.fea.ansys.writing.ansys_process import *
from compas_fea.fea.ansys.writing.ansys_steps import *
from compas_fea.fea.ansys.writing.ansys_forces import *


# Author(s): Tomas Mendez Echenagucia (github.com/tmsmendez)


def write_static_analysis_request(structure, path, name):
    filename = name + '.txt'
    ansys_open_pre_process(path, filename)
    write_all_materials(structure, path, filename)
    write_nodes(structure, path, filename)
    write_elements(structure, path, filename)
    loads = []
    for skey in structure.steps_order:
        displacements = structure.steps[skey].displacements
        factor = structure.steps[skey].factor
        loads.extend(structure.steps[skey].loads)
        write_static_solve(structure, path, filename, skey)
        write_constraint_nodes(structure, path, filename, displacements)
        write_loads(structure, path, filename, loads, factor)
        write_request_load_step_file(structure, path, filename)
    write_request_solve_steps(structure, path, filename)


def write_static_solve(structure, path, filename, skey):
    cFile = open(os.path.join(path, filename), 'a')
    cFile.write('! \n')
    cFile.write('/SOLU ! \n')
    cFile.write('ERESX, NO \n')  # this copies IP results to nodes
    cFile.write('ANTYPE,0\n')
    cFile.write('!\n')
    if structure.steps[skey].nlgeom:
        cFile.write('NLGEOM,ON\n')  # add automatic time steps and max substeps/increments
        cFile.write('NSUBST,20,1000,1\n')
        cFile.write('AUTOTS,1\n')
        cFile.write('!\n')
    cFile.close()


def write_static_results_from_ansys_rst(structure, fields, step_index=0):

    if type(fields) == str:
        fields = [fields]
    if 'u' in fields or 'all' in fields:
        write_request_node_displacements(structure, step_index)
    if 'sf' in fields or 'all' in fields:
        write_request_element_forces(structure, step_index)
    if 's' in fields or 'all' in fields:
        # write_request_nodal_stresses(structure, step_index)
        write_request_element_stresses(structure, step_index)






    if 'sp' in fields or 'all' in fields:
        write_request_pricipal_stresses(path, name, step_name)
    if 'ss' in fields or 'all' in fields:
        write_request_shear_stresses(path, name, step_name)
    if 'e' in fields or 'all' in fields:
        write_request_principal_strains(path, name, step_name)
    if 'rf' in fields or 'all' in fields:
        write_request_reactions(path, name, step_name)

