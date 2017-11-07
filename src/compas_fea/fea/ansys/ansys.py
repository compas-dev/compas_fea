import os
import shutil
import subprocess

from compas_fea.fea.ansys.writing import *
from compas_fea.fea.ansys.reading import *

__author__     = ['Tomas Mendez Echenagucia <mendez@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'mendez@arch.ethz.ch'


__all__ = [
    'input_generate',
    'make_command_file_static',
    'make_command_file_modal',
    'make_command_file_harmonic',
    'ansys_launch_process',
    'delete_result_files',
    'write_total_results',
    'write_static_results_from_ansys_rst'
]


def input_generate(structure):
    name = structure.name
    path = structure.path
    stypes = [structure.steps[skey].type for skey in structure.steps]

    if 'STATIC' in stypes:
        make_command_file_static(structure, path, name)
    elif 'MODAL' in stypes:
        make_command_file_modal(structure, path, name)
    elif 'HARMONIC' in stypes:
        make_command_file_harmonic(structure, path, name, skey)
    else:
        raise ValueError('This analysis type has not yet been implemented for Compas Ansys')


def make_command_file_static(structure, path, name):

    write_static_analysis_request(structure, path, name)


def make_command_file_modal(structure, path, name):

    write_modal_analysis_request(structure, path, name)


def make_command_file_harmonic(structure, output_path, filename, skey):

    write_harmonic_analysis_request(structure, output_path, filename, skey)


def ansys_launch_process(path, name, fields, cpus, license, delete=True):

    if not os.path.exists(path + name + '_output/'):
        os.makedirs(path + name + '_output/')
    elif delete:
        delete_result_files(path, name)

    ansys_path = 'MAPDL.exe'
    inp_path = path + '/' + name + '.txt'
    work_dir = path + name + '_output/'

    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
    out_path = work_dir + '/' + name + '.out'

    if license == 'research':
        lic_str = 'aa_r'
    elif license == 'student':
        lic_str = 'aa_t_a'
    else:
        lic_str = 'aa_t_a'  # temporary default.

    launch_string = '\"' + ansys_path + '\" -p ' + lic_str + ' -np ' + str(cpus)
    launch_string += ' -dir \"' + work_dir
    launch_string += '\" -j \"' + name + '\" -s read -l en-us -b -i \"'
    launch_string += inp_path + ' \" -o \"' + out_path + '\"'

    subprocess.call(launch_string)


def ansys_launch_process_extract(path, name, cpus=2, license='research'):

    ansys_path = 'MAPDL.exe'
    inp_path = path + '/' + name + '_extract.txt'
    work_dir = path + name + '_output/'
    out_path = work_dir + '/output_extract.out'

    if license == 'research':
        lic_str = 'aa_r'
    elif license == 'student':
        lic_str = 'aa_t_a'
    else:
        lic_str = 'aa_t_a'  # temporary default.

    launch_string = '\"' + ansys_path + '\" -p ' + lic_str + ' -np ' + str(cpus)
    launch_string += ' -dir \"' + work_dir
    launch_string += '\" -j \"' + name + '\" -s read -l en-us -b -i \"'
    launch_string += inp_path + ' \" -o \"' + out_path + '\"'
    subprocess.call(launch_string)


def delete_result_files(path, filename):
    out_path = path + '/' + filename + '_output/'
    shutil.rmtree(out_path)


def write_total_results(filename, output_path, excluded_nodes=None, node_disp=None):

    r_file = open(output_path + '/' + str(filename), 'w')

    try:
        stresses_file   = open(output_path + 'nodal_stresses_.txt', 'r')
    except:
        stresses_file = None
    try:
        p_stresses_file   = open(output_path + 'principal_stresses_.txt', 'r')
    except:
        p_stresses_file = None
    try:
        shear_stresses_file   = open(output_path + 'shear_stresses_.txt', 'r')
    except:
        shear_stresses_file = None
    try:
        displacements_file = open(output_path + 'displacements.txt', 'r')
    except:
        displacements_file = None

    stresses = stresses_file.readlines()
    p_stresses = p_stresses_file.readlines()
    shear_stresses = shear_stresses_file.readlines()
    displacements = displacements_file.readlines()

    if excluded_nodes:
        nodes = sorted(excluded_nodes)
        for i in range(len(nodes)):
            node = nodes[-1 - i]
            del stresses[node]
            del p_stresses[node]
            del shear_stresses[node]
            del displacements[node]

    s = []
    for stress in stresses:
        stressString = stress.split(',')
        del stressString[0]
        for string in stressString:
            try:
                temp = float(string)
            except:
                pass
            s.append(temp)

    ps = []
    for stress in p_stresses:
        stressString = stress.split(',')
        del stressString[0]
        for string in stressString:
            try:
                temp = float(string)
            except:
                pass
            ps.append(temp)

    ss = []
    for stress in shear_stresses:
        stressString = stress.split(',')
        del stressString[0]
        for string in stressString:
            try:
                temp = float(string)
            except:
                pass
            ss.append(temp)

    d = []
    for displ in displacements:
        dispString = displ.split(',')
        del dispString[0]
        temp = []
        for string in dispString:
            try:
                temp.append((float(string)))
            except:
                temp = None
        d.append(abs((temp[0]**2 + temp[1]**2 + temp[2]**2)**0.5))

    max_compression = min(s)
    max_tension = max(s)
    max_pcompression = min(ps)
    max_ptension = max(ps)
    max_scompression = min(ss)
    max_stension = max(ss)
    max_disp = max(d)
    avg_disp = sum(d) / float(len(d))

    r_file.write(str(filename))
    r_file.write(' \n')

    r_file.write('maximum compression stress,')
    r_file.write(str(max_compression))
    r_file.write(' \n')

    r_file.write('maximum tension stress,')
    r_file.write(str(max_tension))
    r_file.write(' \n')

    r_file.write('maximum principal compression stress,')
    r_file.write(str(max_pcompression))
    r_file.write(' \n')

    r_file.write('maximum principal tension stress,')
    r_file.write(str(max_ptension))
    r_file.write(' \n')

    r_file.write('maximum shear compression stress,')
    r_file.write(str(max_scompression))
    r_file.write(' \n')

    r_file.write('maximum shear tension stress,')
    r_file.write(str(max_stension))
    r_file.write(' \n')

    r_file.write('maximum displacement,')
    r_file.write(str(max_disp))
    r_file.write(' \n')

    r_file.write('average displacement,')
    r_file.write(str(avg_disp))
    r_file.write(' \n')

    if node_disp:
        r_file.write('displacement node '+str(node_disp)+' \n')
        r_file.write(str(d[int(node_disp)]))
        r_file.write(' \n')
        r_file.write(' \n')

    r_file.close()


def extract_rst_data(structure, fields='all', steps='last'):
    write_results_from_rst(structure, fields, steps)
    load_to_results(structure, fields, steps)


def write_results_from_rst(structure, fields, steps):
    filename = structure.name + '_extract.txt'
    path = structure.path
    if steps == 'last':
        steps = [structure.steps_order[-1]]
    elif steps == 'all':
        steps = structure.steps_order
    ansys_open_post_process(path, filename)
    for skey in steps:
        step_index = steps.index(skey)
        stype = structure.steps[skey].type
        if stype == 'STATIC':
            set_current_step(path, filename, step_index=step_index)
            write_static_results_from_ansys_rst(structure.name, path, fields,
                                                step_index=step_index, step_name=skey)
        elif stype == 'MODAL':
            num_modes = structure.steps[skey].modes
            write_modal_results_from_ansys_rst(structure.name, path, fields, num_modes,
                                               step_index=step_index, step_name=skey)
        elif stype == 'HARMONIC':
            pass
    ansys_launch_process_extract(path, structure.name)
    os.remove(path + '/' + filename)


def load_to_results(structure, fields, steps):
    out_path = structure.path + structure.name + '_output/'
    if steps == 'all':
        steps = structure.steps.keys()
    elif steps == 'last':
        steps = [structure.steps_order[-1]]
    elif type(steps) == str:
        steps = [steps]

    for step in steps:
        if structure.steps[step].__name__ == 'StaticStep':
            rdict = []
            if 'u' in fields or 'all' in fields:
                rdict.append(get_displacements_from_result_files(out_path, step))
            if 's' in fields or 'all' in fields:
                rdict.append(get_nodal_stresses_from_result_files(out_path, step))
            if 'r' in fields or 'all' in fields:
                rdict.append(get_reactions_from_result_files(out_path, step))
            if 'e' in fields or 'all' in fields:
                rdict.append(get_principal_strains_from_result_files(out_path, step))
            if 'sp' in fields or 'all' in fields:
                rdict.append(get_principal_stresses_from_result_files(out_path, step))
            if 'ss' in fields or 'all' in fields:
                rdict.append(get_shear_stresses_from_result_files(out_path, step))
        elif structure.steps[step].__name__ == 'ModalStep':
            rdict = []
            if 'u' in fields or 'all' in fields:
                rdict.append(get_modal_shapes_from_result_files(out_path))
            if 'f' in fields or 'all' in fields:
                fdict = get_modal_freq_from_result_files(out_path)
                structure.results['frequency'] = fdict

        structure.results['nodal'][step] = rdict[0]
        if len(rdict) >= 1:
            for d in rdict[1:]:
                for key, att in structure.results['nodal'][step].items():
                    att.update(d[key])


