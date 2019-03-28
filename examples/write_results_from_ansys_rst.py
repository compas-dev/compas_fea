import os
from compas_fea.fea.ansys import write_static_results_from_ansys_rst


# Author(s): Tomás Méndez Echenagucia (github.com/tmsmendez)


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
