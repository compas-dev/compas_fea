import os


# Author(s): Tomas Mendez Echenagucia (github.com/tmsmendez)


def ansys_open_pre_process(path, filename):
    cFile = open(os.path.join(path, filename), 'w')
    cFile.write('! Ansys command file written from compas_fea \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.write('/PREP7 \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def ansys_open_post_process(path, filename):
    cFile = open(os.path.join(path, filename), 'w')
    cFile.write('! Ansys post-process file written from compas_fea DUDE\n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.write('/POST1 \n')
    cFile.write('!\n')
    cFile.close()


def write_etable_restart(structure):
    name = structure.name
    path = structure.path
    filename = name + '_extract.txt'
    fh = open(os.path.join(path, filename), 'a')
    fh.write('ESEL, ALL \n')
    fh.write('ETABLE, ERAS \n')
    fh.write('! \n')
    fh.close()


def write_request_write_array(structure, fname, out_path, aname, alen, awidth, index_name=None, header=None):

    # Include header string

    name = structure.name
    path = structure.path

    out_path = os.path.join(path, name + '_output')
    filename = name + '_extract.txt'

    fh = open(os.path.join(path, filename), 'a')
    fh.write('adiv = \',\' \n')
    fh.write('*cfopen,' + out_path + '/' + fname + ',txt \n')

    fh.write('*do, i, 1, {0} \n'.format(awidth))
    fh.write('*vwrite')
    if index_name:
        fh.write(', {0}(i), adiv'.format(index_name))
    for i in range(alen):
        fh.write(', {0}({1}, i)'.format(aname, i + 1))
        if i == alen - 1:
            break
        fh.write(', adiv')
    fh.write('\n')

    fh.write('(')
    if index_name:
        fh.write('F9.0, A, ')
    for i in range(alen):
        # fh.write('ES, A ')  # this should be float 64
        fh.write(', E14.8')  # this should be float 32 but needs to be checked for many values and speed
        if i == alen - 1:
            break
        fh.write(', A')
    fh.write(') \n')
    fh.write('*Enddo \n')

    fh.write('*cfclose \n')
    fh.write('!\n')
    fh.close()
