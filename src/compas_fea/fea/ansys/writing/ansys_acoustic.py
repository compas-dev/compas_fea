import os
from .ansys_nodes_elements import write_constraint_nodes
from .ansys_nodes_elements import write_nodes
from .ansys_nodes_elements import write_elements
from .ansys_materials import write_all_materials
from .ansys_loads import write_loads
from compas_fea.fea.ansys.writing.ansys_process import *
from compas_fea.fea.ansys.writing.ansys_steps import *
from compas_fea.fea.ansys.writing.ansys_nodes_elements import *

__author__ = ['Tomas Mendez Echenagucia <mendez@arch.ethz.ch>']
__copyright__ = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__ = 'MIT License'
__email__ = 'mendez@arch.ethz.ch'


def write_acoustic_analysis_request(structure, path, name, skey):

    filename = name + '.txt'
    ansys_open_pre_process(path, filename)
    write_all_materials(structure, path, filename)
    write_nodes(structure, path, filename)
    write_elements(structure, path, filename)
    skey = structure.steps_order[0]
    if structure.steps[skey].type == 'acoustic':
        displacements = structure.steps[skey].displacements
        factor = structure.steps[skey].factor
        loads = structure.steps[skey].loads
        write_constraint_nodes(structure, path, filename, displacements)
        write_radiating_elements(structure, path, filename, skey)
        write_loads(structure, path, filename, loads, factor)
        write_acoustic_solve(structure, path, filename, skey)


def write_radiating_elements(structure, output_path, filename, skey):
    rad_list = structure.steps[skey].sources
    cFile = open(os.path.join(output_path, filename), 'a')
    strings = []
    for rad in rad_list:
        if type(rad) == int:
            rad = str(rad + 1)
            strings.append('SF, {0}, MXWF,           ! Radiating surfaces \n'.format(rad))
        elif type(rad) == str:
            rads = structure.sets[rad]['selection']
            for rad in rads:
                strings.append('SF, {0}, MXWF,           ! Radiating surfaces \n'.format(rad))
    for string in strings:
        cFile.write(string)
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_acoustic_solve(structure, output_path, filename, skey):
    freq_list = structure.steps[skey].freq_list
    harmonic_damping = structure.steps[skey].damping
    sind = structure.steps_order.index(skey)
    samples = structure.steps[skey].samples

    n = 10
    freq_list_ = [freq_list[i:i + n] for i in range(0, len(freq_list), n)]

    cFile = open(os.path.join(output_path, filename), 'a')

    cFile.write('/SOL \n')
    cFile.write('ANTYPE,3            ! Harmonic analysis \n')

    cFile.write('*dim, freq_list{0}, array, {1} \n'.format(sind, len(freq_list)))
    for i, freq in enumerate(freq_list_):
        cFile.write('freq_list{0}('.format(sind) + str(i * n + 1) + ') = ' + ', '.join([str(f) for f in freq]) + '\n')
    cFile.write('HARFRQ, , , , , %freq_list{0}%, , ! Frequency range / list \n'.format(sind))
    cFile.write('KBC,1                ! Stepped loads \n')

    if harmonic_damping:
        # cFile.write('ALPHAD,'+ str(harmonic_damping)+'   ! mass matrix multiplier for damping \n')
        cFile.write('BETAD,' + str(harmonic_damping) + '   ! stiffness matrix multiplier for damping \n')
        # cFile.write('DMPRAT,' + str(harmonic_damping) + '   ! constant modal damping ratio \n')

    string = 'MSOLVE, {0}, , ,\n'.format(samples)
    cFile.write(string)
    cFile.write('FINISH \n')
    cFile.write('!\n')
    cFile.write('/POST1 \n')
    cFile.write('PLST, tl_results, txt, dfst, 0 \n')
    cFile.write('FINISH \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()
