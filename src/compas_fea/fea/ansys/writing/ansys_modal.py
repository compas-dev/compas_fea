import os
from .ansys_nodes_elements import write_request_node_displacements
from .ansys_nodes_elements import write_constraint_nodes
from .ansys_nodes_elements import write_nodes
from .ansys_nodes_elements import write_elements
from .ansys_materials import write_all_materials
from compas_fea.fea.ansys.writing.ansys_process import ansys_open_pre_process
from compas_fea.fea.ansys.writing.ansys_steps import write_request_load_step_file
from compas_fea.fea.ansys.writing.ansys_steps import write_request_solve_steps
from compas_fea.fea.ansys.writing.ansys_nodes_elements import write_request_element_nodes


# Author(s): Tomas Mendez Echenagucia (github.com/tmsmendez)


def write_modal_analysis_request(structure, path, name):
    filename = name + '.txt'
    ansys_open_pre_process(path, filename)
    write_all_materials(structure, path, filename)
    write_nodes(structure, path, filename)
    write_elements(structure, path, filename)
    for skey in structure.steps_order:
        if structure.steps[skey].type == 'modal':
            displacements = structure.steps[skey].displacements
            write_modal_solve(structure, path, filename, skey)
            write_constraint_nodes(structure, path, filename, displacements)
            write_request_load_step_file(structure, path, filename)
    write_request_solve_steps(structure, path, filename)


def write_modal_solve(structure, path, filename, skey):
    num_modes = structure.steps[skey].modes
    cFile = open(os.path.join(path, filename), 'a')
    cFile.write('/SOL \n')
    cFile.write('!\n')
    cFile.write('ANTYPE,2 \n')

    cFile.write('MODOPT,LANB,' + str(num_modes) + ' \n')
    cFile.write('EQSLV,SPAR \n')
    cFile.write('MXPAND,' + str(num_modes) + ', , ,1 \n')
    cFile.write('LUMPM,0 \n')
    cFile.write('PSTRES,0 \n')
    cFile.write('!\n')
    cFile.write('!\n')

    # if structure.geom_nonlinearity is True:
    #     cFile.close()
    #     write_geom_nonlinearity(path, filename)
    #     cFile = open(path + "/" + filename, 'a')

    # cFile.write('SOLVE')
    # cFile.write('!\n')
    # cFile.write('!\n')
    cFile.close()


def write_modal_post_process(path, name, step_index):
    filename = name + '_extract.txt'
    cFile = open(os.path.join(path, filename), 'a')
    cFile.write('/POST1 \n')
    cFile.write('SET,' + str(step_index + 1) + '\n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_request_modal_freq(path, name, skey, num_modes, step_index):
    out_path = os.path.join(path, name + '_output')
    filename = name + '_extract.txt'

    cFile = open(os.path.join(path, filename), 'a')
    cFile.write('!\n')
    cFile.write('/POST1 \n')
    cFile.write('*set,n_freq, \n')
    cFile.write('*dim,n_freq,array,' + str(num_modes) + ', \n')

    for i in range(num_modes):
        cFile.write('SET,' + str(step_index + 1) + ',' + str(i + 1) + '\n')
        cFile.write('*GET,n_freq(' + str(i + 1) + '),ACTIVE, 0, SET, FREQ \n')

    cFile.write('/SOL \n')
    cFile.write('!\n')
    cFile.write('*dim,nds,,' + str(num_modes) + ',1 \n')
    cFile.write('*vfill,nds(1),ramp,1,1 \n')
    cFile.write('*cfopen,' + os.path.join(out_path, 'modal_out', 'modal_freq') + ',txt \n')
    cFile.write('*vwrite, nds(1) , \',\'  , n_freq(1) \n')
    cFile.write('(F8.0, A, ES) \n')
    cFile.write('*cfclose \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_request_modal_shapes(path, name, step_name, num_modes, step_index):
    filename = name + '_extract.txt'

    cFile = open(os.path.join(path, filename), 'a')
    cFile.write('/POST1 \n')
    cFile.close()
    for i in range(num_modes):
        cFile = open(os.path.join(path, filename), 'a')
        # cFile.write('SET,' + str(step_index + 1) + ' \n')
        cFile.write('SET,' + str(step_index + 1) + ',' + str(i + 1) + '\n')
        cFile.write('! Mode ' + str(i + 1) + ' \n \n \n')
        cFile.close()
        write_request_node_displacements(path, name, step_name, mode=i + 1)


def write_modal_results_from_ansys_rst(name, path, fields, num_modes, step_index=0, step_name='step'):
    if not os.path.exists(os.path.join(path, name + '_output', 'modal_out')):
        os.makedirs(os.path.join(path, name + '_output', 'modal_out'))

    # write_modal_post_process(path, name, step_index)
    if type(fields) == str:
        fields = [fields]
    if 'u' in fields or 'all' in fields:
        write_request_modal_shapes(path, name, step_name, num_modes, step_index)
    if 'f' in fields or 'all' in fields:
        write_request_modal_freq(path, name, step_name, num_modes, step_index)
    if 'geo' in fields:
        write_request_element_nodes(path, name)
