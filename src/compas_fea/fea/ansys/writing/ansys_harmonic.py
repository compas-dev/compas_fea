import os
from .ansys_nodes_elements import write_constraint_nodes
from .ansys_nodes_elements import write_nodes
from .ansys_nodes_elements import write_elements
from .ansys_materials import write_all_materials
from .ansys_loads import write_loads
from compas_fea.fea.ansys.writing.ansys_process import ansys_open_pre_process
from compas_fea.fea.ansys.writing.ansys_steps import write_request_load_step_file
from compas_fea.fea.ansys.writing.ansys_steps import write_request_solve_steps
from compas_fea.fea.ansys.writing.ansys_nodes_elements import write_request_element_nodes


# Author(s): Tomas Mendez Echenagucia (github.com/tmsmendez)


def write_harmonic_analysis_request(structure, path, name, skey):

    filename = name + '.txt'
    ansys_open_pre_process(path, filename)
    write_all_materials(structure, path, filename)
    write_nodes(structure, path, filename)
    write_elements(structure, path, filename)
    for skey in structure.steps_order:
        if structure.steps[skey].type == 'harmonic':
            displacements = structure.steps[skey].displacements
            factor = structure.steps[skey].factor
            loads = structure.steps[skey].loads
            write_harmonic_solve(structure, path, filename, skey)
            write_loads(structure, path, filename, loads, factor)
            write_constraint_nodes(structure, path, filename, displacements)
            write_request_load_step_file(structure, path, filename)
    write_request_solve_steps(structure, path, filename)


def write_harmonic_solve(structure, output_path, filename, skey):
    freq_list = structure.steps[skey].freq_list
    harmonic_damping = structure.steps[skey].damping
    sind = structure.steps_order.index(skey)

    n = 10
    freq_list_ = [freq_list[i:i + n] for i in range(0, len(freq_list), n)]

    cFile = open(os.path.join(output_path, filename), 'a')
    cFile.write('/SOL \n')
    cFile.write('!\n')
    cFile.write('FINISH \n')
    cFile.write('/SOLU \n')
    cFile.write('ANTYPE,3            ! Harmonic analysis \n')
    cFile.write('*dim, freq_list{0}, array, {1} \n'.format(sind, len(freq_list)))
    for i, freq in enumerate(freq_list_):
        cFile.write('freq_list{0}('.format(sind) + str(i * n + 1) + ') = ' + ', '.join([str(f) for f in freq]) + '\n')
    cFile.write('HARFRQ, , , , , %freq_list{0}%, , ! Frequency range / list \n'.format(sind))
    cFile.write('KBC,1                ! Stepped loads \n')

    if harmonic_damping:
        # cFile.write('ALPHAD,'+ str(harmonic_damping)+'   ! mass matrix multiplier for damping \n')
        # cFile.write('BETAD,' + str(harmonic_damping) + '   ! stiffness matrix multiplier for damping \n')
        cFile.write('DMPRAT,' + str(harmonic_damping) + '   ! constant modal damping ratio \n')

    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_harmonic_results_from_ansys_rst(name, path, fields, freq_list, step_index=0, step_name='step', sets=None):

    step_folder = 'harmonic_out'
    if not os.path.exists(os.path.join(path, name + '_output', step_folder)):
        os.makedirs(os.path.join(path, name + '_output', step_folder))

    # write_harmonic_post_process(path, name)

    if type(fields) == str:
        fields = [fields]
    if 'u' in fields or 'all' in fields:
        if len(freq_list) == 1:
            freq = freq_list[0]
            write_request_complex_displacements(path, name, freq, step_index)
        else:
            write_request_per_freq_nodal_displacements(path, name, freq_list, step_index, sets)
        # write_something(path, name)
    if 'geo' in fields or 'all' in fields:
        write_request_element_nodes(path, name)


def write_harmonic_post_process(path, name):
    filename = name + '_extract.txt'
    cFile = open(os.path.join(path, filename), 'a')
    cFile.write('/POST26 \n')
    cFile.write('PRCPLX, 0 \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_request_per_freq_nodal_displacements(path, name, freq_list, step_index, sets=None):

    step_folder = 'harmonic_out_{}'.format(step_index)
    filename = name + '_extract.txt'
    harmonic_outpath = os.path.join(path, name + '_output', step_folder)

    cFile = open(os.path.join(path, filename), 'a')

    if sets:
        cFile.write('/POST1 \n')
        cFile.write('SET, {}, \n'.format(step_index + 1))
        cFile.write('/POST26 \n')
        cFile.write('PRCPLX, 0 \n')
        cFile.write('!\n')
        cFile.write('!\n')

        for n in sets:
            cFile.write('curr_n=' + str(n + 1) + ' \n')
            cFile.write('nsol,2,curr_n,u,x ! output UX \n')
            cFile.write('nsol,3,curr_n,u,y ! output UY \n')
            cFile.write('nsol,4,curr_n,u,z ! output UZ \n')

            cFile.write('*dim,N%curr_n%_output,array,' + str(len(freq_list)) + ',7 \n')

            cFile.write('vget,N%curr_n%_output(1,1),1 ! put time in array \n')
            cFile.write('vget,N%curr_n%_output(1,2),2,,0 ! put UX in array \n')
            cFile.write('vget,N%curr_n%_output(1,3),3,,0 ! put UY in array \n')
            cFile.write('vget,N%curr_n%_output(1,4),4,,0 ! put UZ in array \n')

            cFile.write('vget,N%curr_n%_output(1,5),2,,1 ! put UX in array \n')
            cFile.write('vget,N%curr_n%_output(1,6),3,,1 ! put UY in array \n')
            cFile.write('vget,N%curr_n%_output(1,7),4,,1 ! put UZ in array \n')

            cFile.write('*cfopen,' + harmonic_outpath + '/node_real_%curr_n%,txt \n')
            cFile.write('*vwrite,N%curr_n%_output(1,1),\',\' ,N%curr_n%_output(1,2),\',\' ,')
            cFile.write('N%curr_n%_output(1,3),\',\' ,N%curr_n%_output(1,4) \n')
            cFile.write('(F8.0, A, E12.5, A, E12.5, A, E12.5, A, E12.5)  \n')
            cFile.write('*cfclose\n')

            cFile.write('*cfopen,' + harmonic_outpath + '/node_imag_%curr_n%,txt \n')
            cFile.write('*vwrite,N%curr_n%_output(1,1),\',\' ,N%curr_n%_output(1,5),\',\' ')
            cFile.write(' ,N%curr_n%_output(1,6),\',\' ,N%curr_n%_output(1,7)\n')
            cFile.write('(F8.0, A, E12.5, A, E12.5, A, E12.5, A, E12.5)  \n')
            cFile.write('*cfclose\n')
            cFile.write('!\n')
            cFile.write('!\n')
            cFile.write('!\n')
            cFile.write('!\n')

    else:
        cFile.write('/POST1 \n')
        cFile.write('SET, {}, \n'.format(step_index + 1))
        cFile.write('*get,num_n,NODE,0,COUNT ! get number of nodes \n')
        cFile.write('*get,n_min,NODE,0,NUM,MIN ! get min node number \n')

        cFile.write('/POST26 \n')
        cFile.write('PRCPLX, 0 \n')
        cFile.write('!\n')
        cFile.write('!\n')

        cFile.write('*do,i,1,num_n,1   ! output to ascii by looping over nodes \n')
        cFile.write('curr_n=n_min \n')
        cFile.write('nsol,2,curr_n,u,x ! output UX \n')
        cFile.write('nsol,3,curr_n,u,y ! output UY \n')
        cFile.write('nsol,4,curr_n,u,z ! output UZ \n')

        cFile.write('*dim,N%curr_n%_output,array,' + str(len(freq_list)) + ',7 \n')

        cFile.write('vget,N%curr_n%_output(1,1),1 ! put time in array \n')
        cFile.write('vget,N%curr_n%_output(1,2),2,,0 ! put UX in array \n')
        cFile.write('vget,N%curr_n%_output(1,3),3,,0 ! put UY in array \n')
        cFile.write('vget,N%curr_n%_output(1,4),4,,0 ! put UZ in array \n')

        cFile.write('vget,N%curr_n%_output(1,5),2,,1 ! put UX in array \n')
        cFile.write('vget,N%curr_n%_output(1,6),3,,1 ! put UY in array \n')
        cFile.write('vget,N%curr_n%_output(1,7),4,,1 ! put UZ in array \n')

        cFile.write('*cfopen,' + harmonic_outpath + '/node_real_%curr_n%,txt \n')
        cFile.write('*vwrite,N%curr_n%_output(1,1),\',\' ,N%curr_n%_output(1,2),\',\' ,')
        cFile.write('N%curr_n%_output(1,3),\',\' ,N%curr_n%_output(1,4) \n')
        cFile.write('(F8.0, A, E12.5, A, E12.5, A, E12.5, A, E12.5)  \n')
        cFile.write('*cfclose\n')

        cFile.write('*cfopen,' + harmonic_outpath + '/node_imag_%curr_n%,txt \n')
        cFile.write('*vwrite,N%curr_n%_output(1,1),\',\' ,N%curr_n%_output(1,5),\',\' ')
        cFile.write(' ,N%curr_n%_output(1,6),\',\' ,N%curr_n%_output(1,7)\n')
        cFile.write('(F8.0, A, E12.5, A, E12.5, A, E12.5, A, E12.5)  \n')
        cFile.write('*cfclose\n')

        cFile.write('*get,n_min,NODE,curr_n,NXTH \n')
        cFile.write('*enddo \n')
        cFile.write('!\n')
        cFile.write('!\n')
    cFile.close()


def write_request_complex_displacements(path, name, freq, step_index):

    step_folder = 'harmonic_out_{}'.format(step_index)
    filename = name + '_extract.txt'
    harmonic_outpath = os.path.join(path, name + '_output', step_folder)

    fname_real = 'harmonic_disp_real_{0}_Hz'.format(freq)
    fname_imag = 'harmonic_disp_imag_{0}_Hz'.format(freq)
    name_ = 'nds_d' + str(freq)
    name_x = 'dispX' + str(freq)
    name_y = 'dispY' + str(freq)
    name_z = 'dispZ' + str(freq)

    cFile = open(os.path.join(path, filename), 'a')
    cFile.write('/POST1 \n')
    cFile.write('!\n')
    cFile.write('SET, {0}, , , 0!\n'.format(step_index + 1))
    cFile.write('*get,numNodes,node,,count \n')
    cFile.write('*set,' + name_x + ', \n')
    cFile.write('*dim,' + name_x + ',array,numNodes,1 \n')
    cFile.write('*set,' + name_y + ', \n')
    cFile.write('*dim,' + name_y + ',array,numNodes,1 \n')
    cFile.write('*set,' + name_z + ', \n')
    cFile.write('*dim,' + name_z + ',array,numNodes,1 \n')
    cFile.write('*dim,' + name_ + ', ,numNodes \n')
    cFile.write('*VGET, ' + name_x + ', node, all, u, X,,,2 \n')
    cFile.write('*VGET, ' + name_y + ', node, all, u, Y,,,2 \n')
    cFile.write('*VGET, ' + name_z + ', node, all, u, Z,,,2 \n')
    cFile.write('*vfill,' + name_ + '(1),ramp,1,1 \n')
    cFile.write('*cfopen,' + harmonic_outpath + '/' + fname_real + ',txt \n')
    cFile.write('*vwrite, ' + name_ + '(1) , \',\'  , ' + name_x + '(1) , \',\' , ')
    cFile.write(name_y + '(1) , \',\' ,' + name_z + '(1) \n')
    cFile.write('(          F9.0,       A,       ES,           A,          ES,          A,      ES) \n')
    cFile.write('*cfclose \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()

    cFile = open(os.path.join(path, filename), 'a')
    cFile.write('/POST1 \n')
    cFile.write('!\n')
    cFile.write('SET, {0}, , , 1!\n'.format(step_index + 1))
    cFile.write('*get,numNodes,node,,count \n')
    cFile.write('*set,' + name_x + ', \n')
    cFile.write('*dim,' + name_x + ',array,numNodes,1 \n')
    cFile.write('*set,' + name_y + ', \n')
    cFile.write('*dim,' + name_y + ',array,numNodes,1 \n')
    cFile.write('*set,' + name_z + ', \n')
    cFile.write('*dim,' + name_z + ',array,numNodes,1 \n')
    cFile.write('*dim,' + name_ + ', ,numNodes \n')
    cFile.write('*VGET, ' + name_x + ', node, all, u, X,,,2 \n')
    cFile.write('*VGET, ' + name_y + ', node, all, u, Y,,,2 \n')
    cFile.write('*VGET, ' + name_z + ', node, all, u, Z,,,2 \n')
    cFile.write('*vfill,' + name_ + '(1),ramp,1,1 \n')
    cFile.write('*cfopen,' + harmonic_outpath + '/' + fname_imag + ',txt \n')
    cFile.write('*vwrite, ' + name_ + '(1) , \',\'  , ' + name_x + '(1) , \',\' , ')
    cFile.write(name_y + '(1) , \',\' ,' + name_z + '(1) \n')
    cFile.write('(          F9.0,       A,       ES,           A,          ES,          A,      ES) \n')
    cFile.write('*cfclose \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()
