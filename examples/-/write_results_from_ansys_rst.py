import os
from compas_fea.fea.ansys import write_static_results_from_ansys_rst


__author__     = ['Tomas Mendez Echenagucia <mendez@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'mendez@arch.ethz.ch'


output_path = os.path.dirname(os.path.abspath(__file__)) + '/'
filename = 'ansys_static.txt'
fields = ['U', 'RF', 'PE']
step_index = 1
write_static_results_from_ansys_rst(filename,
                                    output_path,
                                    fields,
                                    step_index=step_index,
                                    step_name='step' + str(step_index),
                                    cpus=2,
                                    license='Research')
