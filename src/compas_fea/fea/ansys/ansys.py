import os
import subprocess
import warnings

from compas_fea.fea.ansys.writing import *

__author__     = ['Tomas Mendez Echenagucia <mendez@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'mendez@arch.ethz.ch'


__all__ = [
    'inp_generate',
    'make_command_file_static',
    'make_command_file_static_combined',
    'make_command_file_modal',
    'make_command_file_harmonic',
    'ansys_launch_process',
    'delete_result_files',
    'write_total_results'
]


def inp_generate(structure, filename, out_path, ):
    output_path = out_path
    filename = os.path.basename(filename)
    stypes = [structure.steps[skey].type for skey in structure.steps]

    if 'STATIC' in stypes:
        static_step_key = structure.combine_static_steps()
        make_command_file_static_combined(structure, output_path, filename, static_step_key)
    elif 'MODAL' in stypes:
        make_command_file_modal(structure, output_path, filename, skey)
    elif 'HARMONIC' in stypes:
        make_command_file_harmonic(structure, output_path, filename, skey)


def make_command_file_static(structure, output_path, filename):
    # write_preprocess(output_path, filename)
    # write_all_materials(structure, output_path, filename)
    # write_nodes(structure, output_path, filename)
    # write_elements(structure, output_path, filename)
    skeys = structure.steps['order']
    steps = structure.steps
    nlgeom_list = [steps[skey].nlgeom for skey in skeys]
    if True in nlgeom_list:
        nlgeom = True
        if not all(i is True for i in nlgeom_list):
            warnings.warn('WARNING: Ansys only allows nlgeom to be ON or OFF for all load steps')
    else:
        nlgeom = False

    for skey in skeys:
        step = steps[skey]
        displacements = step.displacements
        factor = step.factor
        loads = step.loads

        write_constraint_nodes(structure, output_path, filename, displacements, factor)
        write_loads(structure, output_path, filename, loads, factor)
        write_step(output_path, filename, skey, nlgeom)

    write_analysis_request_static(structure, output_path, filename)


def make_command_file_static_combined(structure, output_path, filename, skey):
    step = structure.steps[skey]
    nlgeom = step.nlgeom
    displacements = step.displacements
    factor = step.factor
    loads = step.loads
    write_preprocess(output_path, filename)
    write_all_materials(structure, output_path, filename)
    write_nodes(structure, output_path, filename)
    write_elements(structure, output_path, filename)
    write_constraint_nodes(structure, output_path, filename, displacements)
    write_loads(structure, output_path, filename, loads, factor)
    write_step(output_path, filename, skey, nlgeom)
    write_analysis_request_static(structure, output_path, filename)


def make_command_file_modal(structure, output_path, filename, skey):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    if not os.path.exists(output_path + 'modal_out/'):
        os.makedirs(output_path + 'modal_out/')

    step = structure.steps[skey]
    displacements = step.displacements
    factor = step.factor
    loads = step.loads

    # write_preprocess(output_path, filename)
    # write_all_materials(structure, output_path, filename)
    # write_elements(structure, output_path, filename)
    # write_constraint_nodes(structure, output_path, filename, displacements)
    # write_loads(structure, output_path, filename, loads, factor)
    write_modal_analysis_request(structure, output_path, filename, skey)


def make_command_file_harmonic(structure, output_path, filename, skey):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    if not os.path.exists(output_path + 'harmonic_out/'):
        os.makedirs(output_path + 'harmonic_out/')

    step = structure.steps[skey]
    displacements = step.displacements
    factor = step.factor
    loads = step.loads

    write_preprocess(output_path, filename)
    write_all_materials(structure, output_path, filename)
    write_elements(structure, output_path, filename)
    write_constraint_nodes(structure, output_path, filename, displacements)
    write_loads(structure, output_path, filename, loads, factor)
    write_harmonic_analysis_request(structure, output_path, filename, skey)


def ansys_launch_process(structure, output_path, filename):
    ansys_path = 'MAPDL.exe'
    delete_result_files(structure, output_path)
    inp_path = output_path + "/" + filename
    work_dir = output_path + "output/"
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
    out_path = work_dir + "/output.out"
    launch_string = "\"" + ansys_path + "\" -p aa_t_a -dir \"" + work_dir
    launch_string += "\" -j \"compas_ansys\" -s read -l en-us -b -i \""
    launch_string += inp_path + " \" -o \"" + out_path + "\""
    subprocess.call(launch_string)


def delete_result_files(structure, output_path):
    filenames = [
        'displacements',
        'elements',
        'nodalStresses',
        'nodes',
        'principalStresses',
        'shear_stresses',
        'principalStrains',
        'reactions',
        'modal_freq'
    ]
    for name in filenames:
        try:
            os.remove(output_path + name + '.txt')
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