import os

from compas_fea.fea.ansys.writing.ansys_process import write_request_write_array
from compas_fea.fea.ansys.writing.ansys_process import write_etable_restart

# Author(s): Tomas Mendez Echenagucia (github.com/tmsmendez)


def write_request_element_forces(structure, step_index):
    for et in structure.et_dict:
        etkey = structure.et_dict[et]
        if et == 'BEAM188':
            write_request_beam_forces(structure, step_index, etkey)
        elif et == 'SHELL181':
            write_request_shell_forces(structure, step_index, etkey)


def write_request_beam_forces(structure, step_index, etkey):
    name = structure.name
    path = structure.path
    step_name = structure.steps_order[step_index]

    out_path = os.path.join(path, name + '_output')
    filename = name + '_extract.txt'

    fh = open(os.path.join(path, filename), 'a')
    fh.write('ESEL, S, TYPE, , {0}, {0} \n'.format(etkey))

    fh.write('*get, nelem, elem,, count \n')

    fh.write('*dim, enum, array, nelem, 1 \n')
    fh.write('*vget, enum, ELEM, , ELIST \n')

    fh.write('ETABLE, , SMISC, 1  \n')  # axial force in node I
    fh.write('ETABLE, , SMISC, 14 \n')  # axial force in node J

    fh.write('ETABLE, , SMISC, 5  \n')  # section force arround Y in node I
    fh.write('ETABLE, , SMISC, 18 \n')  # section force arround Y in node J

    fh.write('ETABLE, , SMISC, 6  \n')  # section force arround X in node I
    fh.write('ETABLE, , SMISC, 19 \n')  # section force arround X in node J

    fh.write('ETABLE, , SMISC, 2  \n')  # bending moments arround X in node I
    fh.write('ETABLE, , SMISC, 15 \n')  # bending moments arround X in node J

    fh.write('ETABLE, , SMISC, 3  \n')  # bending moments arround Y in node I
    fh.write('ETABLE, , SMISC, 16 \n')  # bending moments arround Y in node J

    fh.write('ETABLE, , SMISC, 4  \n')  # torsional moments in node I
    fh.write('ETABLE, , SMISC, 17 \n')  # torsional moments in node J

    fh.write('*dim, eforces, array, nelem, 12 \n')

    fh.write('*do,i,1,nelem \n')
    fh.write('*get, eforces(i,1), ETAB, 1, ELEM, enum(i) \n')
    fh.write('*get, eforces(i,2), ETAB, 2, ELEM, enum(i) \n')
    fh.write('*get, eforces(i,3), ETAB, 3, ELEM, enum(i) \n')
    fh.write('*get, eforces(i,4), ETAB, 4, ELEM, enum(i) \n')
    fh.write('*get, eforces(i,5), ETAB, 5, ELEM, enum(i) \n')
    fh.write('*get, eforces(i,6), ETAB, 6, ELEM, enum(i) \n')
    fh.write('*get, eforces(i,7), ETAB, 7, ELEM, enum(i) \n')
    fh.write('*get, eforces(i,8), ETAB, 8, ELEM, enum(i) \n')
    fh.write('*get, eforces(i,9), ETAB, 9, ELEM, enum(i) \n')
    fh.write('*get, eforces(i,10), ETAB, 10, ELEM, enum(i) \n')
    fh.write('*get, eforces(i,11), ETAB, 11, ELEM, enum(i) \n')
    fh.write('*get, eforces(i,12), ETAB, 12, ELEM, enum(i) \n')
    fh.write('*Enddo \n')

    fname = str(step_name) + '_' + 'beam_forces'
    fh.write('*cfopen,' + out_path + '/' + fname + ',txt \n')
    fh.write('*CFWRITE, forces, E number, axial I, axial J, secYI, secYJ, secXI, secXJ  \n')
    fh.write('*do,i,1,nelem \n')
    fh.write('*CFWRITE, forces, enum(i,1), eforces(i,1), eforces(i,2), eforces(i,3), eforces(i,4), eforces(i,5), eforces(i,6) \n')
    fh.write('*Enddo \n')
    fh.write('! \n')

    fname = str(step_name) + '_' + 'beam_moments'
    fh.write('*cfopen,' + out_path + '/' + fname + ',txt \n')
    fh.write('*CFWRITE, moments, E number, MXI, MXJJ, MYI, MYJ, TorI, TorJ  \n')
    fh.write('*do,i,1,nelem \n')
    fh.write('*CFWRITE, mX, enum(i,1), eforces(i,7), eforces(i,8), eforces(i,9), eforces(i,10), eforces(i,11), eforces(i,12) \n')
    fh.write('*Enddo \n')
    fh.write('! \n')

    fh.write('ESEL, ALL \n')
    fh.write('ETABLE, ERAS \n')
    fh.write('! \n')

    fh.close()


def write_request_shell_forces(structure, step_index, etkey):
    name = structure.name
    path = structure.path
    step_name = structure.steps_order[step_index]

    out_path = os.path.join(path, name + '_output')
    filename = name + '_extract.txt'

    fh = open(os.path.join(path, filename), 'a')
    fh.write('ESEL, S, TYPE, , {0}, {0} \n'.format(etkey))

    fh.write('ETABLE, , SMISC, 1 \n')  # N11 In-plane forces (per unit length)
    fh.write('ETABLE, , SMISC, 2 \n')  # N22 In-plane forces (per unit length)
    fh.write('ETABLE, , SMISC, 3 \n')  # N12 In-plane forces (per unit length)

    fh.write('ETABLE, , SMISC, 4 \n')  # M11 Out-of-plane moments (per unit length)
    fh.write('ETABLE, , SMISC, 5 \n')  # M22 Out-of-plane moments (per unit length)
    fh.write('ETABLE, , SMISC, 6 \n')  # M12 Out-of-plane moments (per unit length)

    fh.write('*get, nelem, elem,, count \n')
    fh.write('*dim, enum, array, nelem, 1 \n')
    fh.write('*dim, eforces, array, 6, nelem \n')
    fh.write('*vget, enum, ELEM, , ELIST \n')

    fh.write('*do,i,1,nelem \n')
    fh.write('*get, eforces(1, i), ETAB, 1, ELEM, enum(i) \n')
    fh.write('*get, eforces(2, i), ETAB, 2, ELEM, enum(i) \n')
    fh.write('*get, eforces(3, i), ETAB, 3, ELEM, enum(i) \n')
    fh.write('*get, eforces(4, i), ETAB, 4, ELEM, enum(i) \n')
    fh.write('*get, eforces(5, i), ETAB, 5, ELEM, enum(i) \n')
    fh.write('*get, eforces(6, i), ETAB, 6, ELEM, enum(i) \n')
    fh.write('*Enddo \n')
    fh.close()

    fname = str(step_name) + '_' + 'shell_forces_moments'
    write_request_write_array(structure, fname, out_path, 'eforces', 6, 4, index_name='enum')
    write_etable_restart(structure)
