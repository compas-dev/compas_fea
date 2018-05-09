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
    'ansys_launch_process_extract',
    'delete_result_files',
    'extract_rst_data',
    'write_results_from_rst',
    'load_to_results'
]


def input_generate(structure):
    """ Generates Ansys input file.

    Parameters:
        structure (obj): Structure object.

    Returns:
        None
    """
    name = structure.name
    path = structure.path
    stypes = [structure.steps[skey].type for skey in structure.steps]

    if 'static' in stypes:
        make_command_file_static(structure, path, name)
    elif 'modal' in stypes:
        make_command_file_modal(structure, path, name)
    elif 'harmonic' in stypes:
        make_command_file_harmonic(structure, path, name, skey)
    else:
        raise ValueError('This analysis type has not yet been implemented for Compas Ansys')


def make_command_file_static(structure, path, name):
    """ Generates Ansys input file for static analysis.

    Parameters:
        structure (obj): Structure object.

    Returns:
        None
    """
    write_static_analysis_request(structure, path, name)


def make_command_file_modal(structure, path, name):
    """ Generates Ansys input file for modal analysis.

    Parameters:
        structure (obj): Structure object.

    Returns:
        None
    """
    write_modal_analysis_request(structure, path, name)


def make_command_file_harmonic(structure, output_path, filename, skey):
    """ Generates Ansys input file for harmonic analysis.

    Parameters:
        structure (obj): Structure object.

    Returns:
        None
    """
    write_harmonic_analysis_request(structure, output_path, filename, skey)


def ansys_launch_process(path, name, cpus, license, delete=True):
    """ Launches an analysis using Ansys.

    Parameters:
        path (str): Path to the Ansys input file.
        name (str): Name of the structure.
        cpus (int): Number of CPU cores to use.
        license (str): Type of Ansys license.
        delete (Bool): Path to the Ansys input file.

    Returns:
        None
    """
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
    # sp = subprocess.Popen(launch_string)
    # sp.wait()
    # sp.terminate()
    # sp.kill()


def ansys_launch_process_extract(path, name, cpus=2, license='research'):
    """ Calls an extraction of results from Ansys.

    Parameters:
        path (str): Path to the Ansys input file.
        name (str): Name of the structure.
        cpus (int): Number of CPU cores to use.
        license (str): Type of Ansys license.

    Returns:
        None
    """
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
    # sp = subprocess.Popen(launch_string)
    # sp.wait()
    # sp.terminate()
    # sp.kill()


def delete_result_files(path, name):
    """ Deletes Ansys result files.

    Parameters:
        path (str): Path to the Ansys input file.
        name (str): Name of the structure.

    Returns:
        None
    """
    out_path = path + '/' + name + '_output/'
    shutil.rmtree(out_path)


def extract_rst_data(structure, fields='all', steps='last'):
    """ Extracts results from Ansys rst file.

    Parameters:
        structure (obj): Structure object.
        fields (list, str): Data field requests.
        steps (list): Loads steps to extract from.

    Returns:
        None
    """
    write_results_from_rst(structure, fields, steps)
    load_to_results(structure, fields, steps)


def write_results_from_rst(structure, fields, steps):
    """ Writes results request file from Ansys.

    Parameters:
        structure (obj): Structure object.
        fields (list, str): Data field requests.
        steps (list): Loads steps to extract from.

    Returns:
        None
    """
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
        if stype == 'static':
            set_current_step(path, filename, step_index=step_index)
            write_static_results_from_ansys_rst(structure.name, path, fields,
                                                step_index=step_index, step_name=skey)
        elif stype == 'modal':
            num_modes = structure.steps[skey].modes
            write_modal_results_from_ansys_rst(structure.name, path, fields, num_modes,
                                               step_index=step_index, step_name=skey)
        elif stype == 'harmonic':
            freq_steps = structure.steps[skey].freq_steps
            write_harmonic_results_from_ansys_rst(structure.name, structure.path, fields, freq_steps, step_index=0, step_name='step')

    ansys_launch_process_extract(path, structure.name)
    # os.remove(path + '/' + filename)


def load_to_results(structure, fields, steps):
    """ Loads results from Ansys txt files to Structure object.

    Parameters:
        structure (obj): Structure object.
        fields (list, str): Data field requests.
        steps (list): Loads steps to extract from.

    Returns:
        None
    """
    out_path = structure.path + structure.name + '_output/'
    if steps == 'all':
        steps = structure.steps.keys()
    elif steps == 'last':
        steps = [structure.steps_order[-1]]
    elif type(steps) == str:
        steps = [steps]

    for step in steps:
        structure.results[step] = {}
        if structure.steps[step].__name__ == 'StaticStep':
            rlist = []
            if 'u' in fields or 'all' in fields:
                rlist.append(get_displacements_from_result_files(out_path, step))
            if 's' in fields or 'all' in fields:
                rlist.append(get_nodal_stresses_from_result_files(out_path, step))
            if 'r' in fields or 'all' in fields:
                rlist.append(get_reactions_from_result_files(out_path, step))
            if 'e' in fields or 'all' in fields:
                rlist.append(get_principal_strains_from_result_files(out_path, step))
            if 'sp' in fields or 'all' in fields:
                rlist.append(get_principal_stresses_from_result_files(out_path, step))
            if 'ss' in fields or 'all' in fields:
                rlist.append(get_shear_stresses_from_result_files(out_path, step))

        elif structure.steps[step].__name__ == 'ModalStep':
            rlist = []
            if 'u' in fields or 'all' in fields:
                rlist.append(get_modal_shapes_from_result_files(out_path))
            if 'f' in fields or 'all' in fields:
                fdict = get_modal_freq_from_result_files(out_path)
                structure.results[step]['frequencies'] = fdict

        elif structure.steps[step].__name__ == 'HarmonicStep':
            rlist = []
            if 'u' in fields or 'all' in fields:
                rlist.append(get_harmonic_data_from_result_files(out_path))

        if 'geo' in fields:
            nodes, elements = get_nodes_elements_from_result_files(out_path)
            structure.nodes = nodes
            for ekey in elements:
                structure.add_element(elements[ekey]['nodes'], elements[ekey]['type'])
        if rlist:
            structure.results[step].setdefault('nodal', rlist[0])
            if len(rlist) >= 1:
                for d in rlist[1:]:
                    for key, att in structure.results[step]['nodal'].items():
                        att.update(d[key])
