import os


# Author(s): Tomás Méndez Echenagucia (github.com/tmsmendez)


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
    cFile.write('! Ansys post-process file written from compas_fea \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.write('/POST1 \n')
    cFile.write('!\n')
    cFile.close()
