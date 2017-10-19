import os
import subprocess

from compas_fea.fea.ansys.writing import *

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
    filename = structure.name
    output_path = structure.path
    stypes = [structure.steps[skey].type for skey in structure.steps]

    if 'STATIC' in stypes:
        make_command_file_static(structure, output_path, filename)
    elif 'MODAL' in stypes:
        make_command_file_modal(structure, output_path, filename, skey)
    elif 'HARMONIC' in stypes:
        make_command_file_harmonic(structure, output_path, filename, skey)
    else:
        raise ValueError('This analysis type has not yet been implemented for Compas Ansys')


def make_command_file_static(structure, output_path, filename):

    write_static_analysis_request(structure, output_path, filename)


def make_command_file_modal(structure, output_path, filename, skey):

    write_modal_analysis_request(structure, output_path, filename, skey)


def make_command_file_harmonic(structure, output_path, filename, skey):

    write_harmonic_analysis_request(structure, output_path, filename, skey)


def ansys_launch_process(output_path, filename, fields, cpus, license):

    if not os.path.exists(output_path + filename + '_output/'):
        os.makedirs(output_path + filename + '_output/')

    ansys_path = 'MAPDL.exe'
    inp_path = output_path + '/' + filename + '.txt'
    work_dir = output_path + filename + '_output/'

    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
    out_path = work_dir + '/output.out'

    if license == 'research':
        lic_str = 'aa_r'
    elif license == 'student':
        lic_str = 'aa_t_a'
    else:
        lic_str = 'aa_t_a'  # temporary default.

    launch_string = '\"' + ansys_path + '\" -p ' + lic_str + ' -np ' + str(cpus)
    launch_string += ' -dir \"' + work_dir
    launch_string += '\" -j \"' + filename + '\" -s read -l en-us -b -i \"'
    launch_string += inp_path + ' \" -o \"' + out_path + '\"'

    subprocess.call(launch_string)


def delete_result_folder(structure, output_path):
    filenames = os.listdir(output_path)
    for name in filenames:
        try:
            os.remove(output_path + name)
        except:
            continue


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


def write_static_results_from_ansys_rst(filename, output_path, step_index=1, step_name='step'):
    write_preprocess(output_path, filename)
    write_post_process(output_path, filename)
    set_current_step(output_path, filename, step_index)
    write_request_element_nodes(output_path, filename)
    write_request_static_results(output_path, filename, step_name)
    ansys_launch_process(output_path, filename)
