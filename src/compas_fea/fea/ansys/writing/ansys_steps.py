__author__     = ['Tomas Mendez Echenagucia <mendez@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'mendez@arch.ethz.ch'


def set_current_step(path, filename, step_index):
    cFile = open(path + filename, 'a')
    cFile.write('! \n')
    cFile.write('/POST1 \n')
    cFile.write('SET, ' + str(step_index + 1) + '! \n')
    cFile.write('!\n')
    cFile.close()


def write_request_load_step_file(structure, output_path, filename):
    cFile = open(output_path + filename, 'a')
    cFile.write('! \n')
    cFile.write('LSWRITE ! \n')
    cFile.write('!\n')
    cFile.close()


def write_request_solve_steps(structure, output_path, filename):
    mstep = len(structure.steps_order)
    cFile = open(output_path + filename, 'a')
    cFile.write('! \n')
    cFile.write('LSSOLVE, 1,' + str(mstep) + ',1! \n')
    cFile.write('!\n')
    cFile.close()
