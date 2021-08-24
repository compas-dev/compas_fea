import os
from .ansys_nodes_elements import write_constraint_nodes
from .ansys_nodes_elements import write_nodes
from .ansys_nodes_elements import write_elements
from .ansys_materials import write_all_materials
from .ansys_loads import write_loads
from compas_fea.fea.ansys.writing.ansys_process import ansys_open_pre_process
from compas_fea.utilities import identify_ranges


# Author(s): Tomas Mendez Echenagucia (github.com/tmsmendez)


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
    rad_elements = structure.steps[skey].sources
    nodes = []
    for ek in rad_elements:
        nodes.extend(structure.elements[ek].nodes)
    ranges = identify_ranges(nodes)

    cFile = open(os.path.join(output_path, filename), 'a')

    for i, r in enumerate(ranges):
        string = 'NSEL, S, NODE, , {0}, {1}, 1,           !  \n'.format(r[0] + 1, r[1] + 1)
        cFile.write(string)
        string = 'CM, nds_cmp_{0}, NODE           !  \n'.format(i)
        cFile.write(string)
        string = 'SF, nds_cmp_{0}, MXWF,           ! Radiating nodes \n'.format(i)
        cFile.write(string)
        cFile.write('!\n')
        cFile.write('NSEL, ALL \n')

    cFile.write('!\n')
    cFile.close()


def write_acoustic_solve(structure, output_path, filename, skey):
    freq_range = structure.steps[skey].freq_range
    freq_step = structure.steps[skey].freq_step
    harmonic_damping = structure.steps[skey].damping
    samples = structure.steps[skey].samples

    cFile = open(os.path.join(output_path, filename), 'a')

    cFile.write('/SOL \n')
    cFile.write('ANTYPE,3            ! Harmonic analysis \n')
    cFile.write('HARFRQ, {0}, {1}, , , , , ! Frequency range / list \n'.format(freq_range[0], freq_range[1]))
    cFile.write('NSUBST, {0} ! number of steps  \n'.format(freq_step))

    if harmonic_damping:
        # cFile.write('ALPHAD,'+ str(harmonic_damping)+'   ! mass matrix multiplier for damping \n')
        # cFile.write('BETAD,' + str(harmonic_damping) + '   ! stiffness matrix multiplier for damping \n')
        cFile.write('DMPRAT,' + str(harmonic_damping) + '   ! constant modal damping ratio \n')

    string = 'MSOLVE, {0}, , ,\n'.format(samples)
    cFile.write(string)
    cFile.write('FINISH \n')
    cFile.write('!\n')

    # request tl results file ----------------------------
    cFile.write('/POST1 \n')
    cFile.write('PLST, {0}_tl_results, txt, dfst, 0 \n'.format(skey))
    cFile.write('FINISH \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()
