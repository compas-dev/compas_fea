from compas_fea.fea.ansys import write_static_results_from_ansys_rst


__author__     = ['Tomas Mendez Echenagucia <mendez@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'mendez@arch.ethz.ch'


output_path = 'C:/Users/user/Documents/ansys_test/'
filename = 'compas_ansys.txt'
write_static_results_from_ansys_rst(filename, output_path, step_index=1, step_name='step')

