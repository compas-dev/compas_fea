import os


# Author(s): Tomas Mendez Echenagucia (github.com/tmsmendez)


def write_request_nodal_stresses(structure, step_index):
    name = structure.name
    path = structure.path
    step_name = structure.steps_order[step_index]

    out_path = os.path.join(path, name + '_output')
    filename = name + '_extract.txt'
    fname = str(step_name) + '_' + 'nodal_stresses'
    name = 'nds_s'

    cFile = open(os.path.join(path, filename), 'a')
    # cFile.write('SET,'+skey+' \n')
    cFile.write('SHELL,TOP  \n')
    cFile.write('*get,numNodes,node,,count \n')
    cFile.write('*set,SXtop, \n')
    cFile.write('*dim,SXtop,array,numNodes,1 \n')
    cFile.write('*set,SYtop, \n')
    cFile.write('*dim,SYtop,array,numNodes,1 \n')
    cFile.write('*set,SZtop, \n')
    cFile.write('*dim,SZtop,array,numNodes,1 \n')
    cFile.write('*dim,' + name + ', ,numNodes \n')
    cFile.write('*VGET, SXtop, node, all, S, X,,,2 \n')
    cFile.write('*VGET, SYtop, node, all, S, Y,,,2 \n')
    cFile.write('*VGET, SZtop, node, all, S, Z,,,2 \n')

    cFile.write('SHELL,BOT  \n')
    cFile.write('*get,numNodes,node,,count \n')
    cFile.write('*set,SXbot, \n')
    cFile.write('*dim,SXbot,array,numNodes,1 \n')
    cFile.write('*set,SYbot, \n')
    cFile.write('*dim,SYbot,array,numNodes,1 \n')
    cFile.write('*set,SZbot, \n')
    cFile.write('*dim,SZbot,array,numNodes,1 \n')
    # cFile.write('*dim,nds, ,numNodes \n')
    cFile.write('*VGET, SXbot, node, all, S, X,,,2 \n')
    cFile.write('*VGET, SYbot, node, all, S, Y,,,2 \n')
    cFile.write('*VGET, SZbot, node, all, S, Z,,,2 \n')

    cFile.write('*vfill,' + name + '(1),ramp,1,1 \n')
    cFile.write('*cfopen,' + out_path + '/' + fname + ',txt \n')
    cFile.write('*vwrite, ' + name + '(1) , \',\'  , SXtop(1) ,   \',\' ,   SYtop(1) ')
    cFile.write(',   \',\' ,  SZtop(1) , \',\',    SXbot(1) ,   \',\' ,   SYbot(1) ,   \',\' ,  SZbot(1) \n')
    cFile.write('(F9.0, A, ES, A, ES, A, ES, A, ES, A, ES, A, ES) \n')
    cFile.write('*cfclose \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()

    # attempt to write averaged nodal stresses (does not work on beams?)
    # fh = open(os.path.join(path, filename), 'a')
    # fh.write('*get, nnodes, node,, count \n')
    # fh.write('*dim, s, array, nnodes, 11 \n')
    # fh.write('! \n')

    # fh.write('*do, i, 1, nnodes \n')
    # fh.write('s(i,1) = i \n')
    # fh.write('*get, s(i,2), NODE, s(i,1), S, X \n')
    # fh.write('*get, s(i,3), NODE, s(i,1), S, Y \n')
    # fh.write('*get, s(i,4), NODE, s(i,1), S, Z \n')
    # fh.write('*get, s(i,5), NODE, s(i,1), S, XX \n')
    # fh.write('*get, s(i,6), NODE, s(i,1), S, YY \n')
    # fh.write('*get, s(i,7), NODE, s(i,1), S, ZZ \n')
    # fh.write('*get, s(i,8), NODE, s(i,1), S, 1 \n')
    # fh.write('*get, s(i,9), NODE, s(i,1), S, 2 \n')
    # fh.write('*get, s(i,10),NODE, s(i,1), S, 3 \n')
    # fh.write('*get, s(i,11),NODE, s(i,1), S, EQV \n')
    # fh.write('*Enddo \n')
    # fh.write('! \n')

    # fh.write('*cfopen,' + out_path + '/' + fname + ',txt \n')

    # fh.write('*do,i,1,nnodes \n')
    # fh.write('*CFWRITE, node S, s(i,1), s(i,2), s(i,3), s(i,4), s(i,5), s(i,6), s(i,7), s(i,8), s(i,9), s(i,10), s(i,11) \n')
    # fh.write('*Enddo \n')
    # fh.close()


def write_request_pricipal_stresses(structure, step_index):
    name = structure.name
    path = structure.path
    step_name = structure.steps_order[step_index]

    out_path = os.path.join(path, name + '_output')
    filename = name + '_extract.txt'
    fname = str(step_name) + '_' + 'principal_stresses'
    name = 'nds_p'
    cFile = open(os.path.join(path, filename), 'a')
    cFile.write('SHELL,TOP  \n')
    cFile.write('*get,numNodes,node,,count \n')
    cFile.write('*set,S1top, \n')
    cFile.write('*dim,S1top,array,numNodes,1 \n')
    cFile.write('*set,S2top, \n')
    cFile.write('*dim,S2top,array,numNodes,1 \n')
    cFile.write('*set,S3top, \n')
    cFile.write('*dim,S3top,array,numNodes,1 \n')
    cFile.write('*dim,' + name + ', ,numNodes \n')
    cFile.write('*VGET, S1top, node, all, S, 1,,,2 \n')
    cFile.write('*VGET, S2top, node, all, S, 2,,,2 \n')
    cFile.write('*VGET, S3top, node, all, S, 3,,,2 \n')

    cFile.write('SHELL,BOT  \n')
    cFile.write('*get,numNodes,node,,count \n')
    cFile.write('*set,S1bot, \n')
    cFile.write('*dim,S1bot,array,numNodes,1 \n')
    cFile.write('*set,S2bot, \n')
    cFile.write('*dim,S2bot,array,numNodes,1 \n')
    cFile.write('*set,S3bot, \n')
    cFile.write('*dim,S3bot,array,numNodes,1 \n')
    # cFile.write('*dim,nds, ,numNodes \n')
    cFile.write('*VGET, S1bot, node, all, S, 1,,,2 \n')
    cFile.write('*VGET, S2bot, node, all, S, 2,,,2 \n')
    cFile.write('*VGET, S3bot, node, all, S, 3,,,2 \n')

    cFile.write('*vfill,' + name + '(1),ramp,1,1 \n')
    cFile.write('*cfopen,' + out_path + '/' + fname + ',txt \n')
    cFile.write('*vwrite, ' + name + '(1), \',\', S1top(1), \',\', S2top(1), \',\',')
    cFile.write(' S3top(1), \',\', S1bot(1), \',\', S2bot(1), \',\', S3bot(1) \n')
    cFile.write('(F9.0, A, ES, A, ES, A, ES, A, ES, A, ES, A, ES) \n')
    cFile.write('*cfclose \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_request_shear_stresses(structure, step_index):
    name = structure.name
    path = structure.path
    step_name = structure.steps_order[step_index]

    out_path = os.path.join(path, name + '_output')
    filename = name + '_extract.txt'
    fname = str(step_name) + '_' + 'shear_stresses'
    name = 'nds_sh'

    cFile = open(os.path.join(path, filename), 'a')
    cFile.write('SHELL,TOP  \n')
    cFile.write('*get,numNodes,node,,count \n')
    cFile.write('*set,S1top, \n')
    cFile.write('*dim,S1top,array,numNodes,1 \n')
    cFile.write('*set,S2top, \n')
    cFile.write('*dim,S2top,array,numNodes,1 \n')
    cFile.write('*set,S3top, \n')
    cFile.write('*dim,S3top,array,numNodes,1 \n')
    cFile.write('*dim,' + name + ', ,numNodes \n')
    cFile.write('*VGET, S1top, node, all, S, XY,,,2 \n')
    cFile.write('*VGET, S2top, node, all, S, YZ,,,2 \n')
    cFile.write('*VGET, S3top, node, all, S, XZ,,,2 \n')

    cFile.write('SHELL,BOT  \n')
    cFile.write('*get,numNodes,node,,count \n')
    cFile.write('*set,S1bot, \n')
    cFile.write('*dim,S1bot,array,numNodes,1 \n')
    cFile.write('*set,S2bot, \n')
    cFile.write('*dim,S2bot,array,numNodes,1 \n')
    cFile.write('*set,S3bot, \n')
    cFile.write('*dim,S3bot,array,numNodes,1 \n')
    # cFile.write('*dim,nds, ,numNodes \n')
    cFile.write('*VGET, S1bot, node, all, S, XY,,,2 \n')
    cFile.write('*VGET, S2bot, node, all, S, YZ,,,2 \n')
    cFile.write('*VGET, S3bot, node, all, S, XZ,,,2 \n')

    cFile.write('*vfill,' + name + '(1),ramp,1,1 \n')
    cFile.write('*cfopen,' + out_path + '/' + fname + ',txt \n')
    cFile.write('*vwrite, ' + name + '(1), \',\', S1top(1), \',\', S2top(1), \',\',')
    cFile.write(' S3top(1), \',\', S1bot(1), \',\', S2bot(1), \',\', S3bot(1) \n')
    cFile.write('(F9.0, A, ES, A, ES, A, ES, A, ES , A, ES, A, ES) \n')
    cFile.write('*cfclose \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_request_principal_strains(structure, step_index):
    name = structure.name
    path = structure.path
    step_name = structure.steps_order[step_index]

    out_path = os.path.join(path, name + '_output')
    filename = name + '_extract.txt'
    fname = str(step_name) + '_' + 'principal_strains'
    name = 'nds_ps'

    cFile = open(os.path.join(path, filename), 'a')
    cFile.write('SHELL,TOP  \n')
    cFile.write('*get,numNodes,node,,count \n')
    cFile.write('*set,S1top, \n')
    cFile.write('*dim,S1top,array,numNodes,1 \n')
    cFile.write('*set,S2top, \n')
    cFile.write('*dim,S2top,array,numNodes,1 \n')
    cFile.write('*set,S3top, \n')
    cFile.write('*dim,S3top,array,numNodes,1 \n')
    cFile.write('*dim,' + name + ', ,numNodes \n')
    cFile.write('*VGET, S1top, node, all, EPTO, 1,,,2 \n')
    cFile.write('*VGET, S2top, node, all, EPTO, 2,,,2 \n')
    cFile.write('*VGET, S3top, node, all, EPTO, 3,,,2 \n')

    cFile.write('SHELL,BOT  \n')
    cFile.write('*get,numNodes,node,,count \n')
    cFile.write('*set,S1bot, \n')
    cFile.write('*dim,S1bot,array,numNodes,1 \n')
    cFile.write('*set,S2bot, \n')
    cFile.write('*dim,S2bot,array,numNodes,1 \n')
    cFile.write('*set,S3bot, \n')
    cFile.write('*dim,S3bot,array,numNodes,1 \n')
    # cFile.write('*dim,nds, ,numNodes \n')
    cFile.write('*VGET, S1bot, node, all, EPTO, 1,,,2 \n')
    cFile.write('*VGET, S2bot, node, all, EPTO, 2,,,2 \n')
    cFile.write('*VGET, S3bot, node, all, EPTO, 3,,,2 \n')

    cFile.write('*vfill,' + name + '(1),ramp,1,1 \n')
    cFile.write('*cfopen,' + out_path + '/' + fname + ',txt \n')
    cFile.write('*vwrite,' + name + '(1), \',\', S1top(1), \',\', S2top(1), \',\',')
    cFile.write(' S3top(1), \',\', S1bot(1), \',\', S2bot(1), \',\', S3bot(1) \n')
    cFile.write('(F9.0, A, ES, A, ES, A, ES, A, ES, A, ES, A, ES) \n')
    cFile.write('*cfclose \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_request_reactions(structure, step_index):
    name = structure.name
    path = structure.path
    step_name = structure.steps_order[step_index]

    out_path = os.path.join(path, name + '_output')
    filename = name + '_extract.txt'
    fname = str(step_name) + '_' + 'reactions'
    name = 'nds_r'

    cFile = open(os.path.join(path, filename), 'a')
    cFile.write('*get,numNodes,node,,count \n')
    cFile.write('*set,RFX, \n')
    cFile.write('*dim,RFX,array,numNodes,1 \n')
    cFile.write('*set,RFY, \n')
    cFile.write('*dim,RFY,array,numNodes,1 \n')
    cFile.write('*set,RFZ, \n')
    cFile.write('*dim,RFZ,array,numNodes,1 \n')

    cFile.write('*set,RMX, \n')
    cFile.write('*dim,RMX,array,numNodes,1 \n')
    cFile.write('*set,RMY, \n')
    cFile.write('*dim,RMY,array,numNodes,1 \n')
    cFile.write('*set,RMZ, \n')
    cFile.write('*dim,RMZ,array,numNodes,1 \n')

    cFile.write('*dim,' + name + ', ,numNodes \n')
    cFile.write('*VGET, RFX, node, all, RF, FX,,,2 \n')
    cFile.write('*VGET, RFY, node, all, RF, FY,,,2 \n')
    cFile.write('*VGET, RFZ, node, all, RF, FZ,,,2 \n')
    cFile.write('*VGET, RMX, node, all, RF, MX,,,2 \n')
    cFile.write('*VGET, RMY, node, all, RF, MY,,,2 \n')
    cFile.write('*VGET, RMZ, node, all, RF, MZ,,,2 \n')

    cFile.write('*vfill,' + name + '(1),ramp,1,1 \n')
    cFile.write('*cfopen,' + out_path + '/' + fname + ',txt \n')
    cFile.write('*vwrite, ' + name + '(1), \',\', RFX(1), \',\', RFY(1), \',\', ')
    cFile.write('RFZ(1), \',\', RMX(1), \',\', RMY(1), \',\', RMZ(1) \n')
    cFile.write('(F9.0, A, ES, A, ES, A, ES, A, ES, A, ES, A, ES) \n')
    cFile.write('*cfclose \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()

    # fh = open(os.path.join(path, filename), 'a')
    # fh.write('*get, nnodes, node,, count \n')
    # fh.write('*dim, r, array, nnodes, 7 \n')
    # fh.write('! \n')

    # fh.write('*do, i, 1, nnodes \n')
    # fh.write('r(i,1) = i                         !Collumn 1 is node number \n')
    # fh.write('*get, r(i,2), NODE, r(i,1), RF, FX   !Collumn 2 is RFX \n')
    # fh.write('*get, r(i,3), NODE, r(i,1), RF, FY   !Collumn 3 is RFY \n')
    # fh.write('*get, r(i,4), NODE, r(i,1), RF, FZ   !Collumn 4 is RFZ \n')
    # fh.write('*get, r(i,5), NODE, r(i,1), RF, MX !Collumn 5 is MX \n')
    # fh.write('*get, r(i,6), NODE, r(i,1), RF, MY !Collumn 5 is MY \n')
    # fh.write('*get, r(i,7), NODE, r(i,1), RF, MZ !Collumn 5 is MZ \n')
    # fh.write('*Enddo \n')
    # fh.write('! \n')

    # fh.write('*cfopen,' + out_path + '/' + fname + ',txt \n')

    # fh.write('*do,i,1,nnodes \n')
    # fh.write('*CFWRITE, node RF, r(i,1), r(i,2), r(i,3), r(i,4), r(i,5), r(i,6), r(i,7) \n')
    # fh.write('*Enddo \n')
    # fh.close()


def write_request_element_stresses(structure, step_index):
    for et in structure.et_dict:
        etkey = structure.et_dict[et]
        if et == 'BEAM188':
            write_request_beam_stresses(structure, step_index, etkey)
        elif et == 'SHELL181':
            write_request_shell_stresses(structure, step_index, etkey)


def write_request_beam_stresses(structure, step_index, etkey):
    # TODO: Shear stresses (s12, s13)

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

    fh.write('ETABLE, , SMISC, 31 \n')  # axial stress (s11) I
    fh.write('ETABLE, , SMISC, 36 \n')  # axial stress (s11) J

    fh.write('ETABLE, , SMISC, 32  \n')  # bending stress TOP in node I
    fh.write('ETABLE, , SMISC, 37 \n')  # bending stress TOP in node J

    fh.write('ETABLE, , SMISC, 33  \n')  # bending stress BOT in node I
    fh.write('ETABLE, , SMISC, 38 \n')  # bending stress BOT in node J

    fh.write('ETABLE, , SMISC, 34  \n')  # bending stress RIGHT in node I
    fh.write('ETABLE, , SMISC, 39 \n')  # bending stress RIGHT in node J

    fh.write('ETABLE, , SMISC, 35  \n')  # bending stress LEFT in node I
    fh.write('ETABLE, , SMISC, 40 \n')  # bending stress LEFT in node J

    fh.write('*dim, estress, array, nelem, 10 \n')

    fh.write('*do,i,1,nelem \n')
    fh.write('*get, estress(i,1), ETAB, 1, ELEM, enum(i) \n')
    fh.write('*get, estress(i,2), ETAB, 2, ELEM, enum(i) \n')
    fh.write('*get, estress(i,3), ETAB, 3, ELEM, enum(i) \n')
    fh.write('*get, estress(i,4), ETAB, 4, ELEM, enum(i) \n')
    fh.write('*get, estress(i,5), ETAB, 5, ELEM, enum(i) \n')
    fh.write('*get, estress(i,6), ETAB, 6, ELEM, enum(i) \n')
    fh.write('*get, estress(i,7), ETAB, 7, ELEM, enum(i) \n')
    fh.write('*get, estress(i,8), ETAB, 8, ELEM, enum(i) \n')
    fh.write('*get, estress(i,9), ETAB, 9, ELEM, enum(i) \n')
    fh.write('*get, estress(i,10), ETAB, 10, ELEM, enum(i) \n')
    fh.write('*Enddo \n')

    fname = str(step_name) + '_' + 'beam_stresses'
    fh.write('*cfopen,' + out_path + '/' + fname + ',txt \n')
    fh.write('*CFWRITE, stresses, E number, S11I, S11J, SByTI, SByTJ, SByBI, SByBJ, SBzTI, SBzTJ, SBzBI, SBzBJ \n')
    fh.write('*do,i,1,nelem \n')
    fh.write('*CFWRITE, stresses, enum(i,1), estress(i,1), estress(i,2),estress(i,3), estress(i,4), estress(i,5), estress(i,6), ')
    fh.write('estress(i,7), estress(i,8), estress(i,9), estress(i,10) \n')
    fh.write('*Enddo \n')

    fh.write('ESEL, ALL \n')
    fh.write('ETABLE, ERAS \n')
    fh.write('! \n')
    fh.close()


def write_request_shell_stresses(structure, step_index, etkey):
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

    fh.write('ETABLE, , SMISC, 34 \n')  # Sm 11 Membrane stresses
    fh.write('ETABLE, , SMISC, 35 \n')  # Sm 22 Membrane stresses
    fh.write('ETABLE, , SMISC, 36 \n')  # Sm 12 Membrane stresses

    fh.write('ETABLE, , SMISC, 37 \n')  # Sb 11 Bending stresses
    fh.write('ETABLE, , SMISC, 38 \n')  # Sb 22 Bending stresses
    fh.write('ETABLE, , SMISC, 39 \n')  # Sb 12 Bending stresses

    fh.write('ETABLE, , SMISC, 40 \n')  # Sp 11 (BOT)Peak stresses
    fh.write('ETABLE, , SMISC, 41 \n')  # Sp 22 (BOT)Peak stresses
    fh.write('ETABLE, , SMISC, 42 \n')  # Sp 12 (BOT)Peak stresses
    fh.write('ETABLE, , SMISC, 43 \n')  # Sp 11 (TOP)Peak stresses
    fh.write('ETABLE, , SMISC, 44 \n')  # Sp 22 (TOP)Peak stresses
    fh.write('ETABLE, , SMISC, 45 \n')  # Sp 12 (TOP)Peak stresses

    fh.write('ETABLE, , SMISC, 46 \n')  # St 13 Transverse stresses
    fh.write('ETABLE, , SMISC, 47 \n')  # St 23 Transverse stresses

    fh.write('*dim, estress, array, nelem, 14 \n')

    fh.write('*do,i,1,nelem \n')
    fh.write('*get, estress(i,1), ETAB, 1, ELEM, enum(i) \n')
    fh.write('*get, estress(i,2), ETAB, 2, ELEM, enum(i) \n')
    fh.write('*get, estress(i,3), ETAB, 3, ELEM, enum(i) \n')
    fh.write('*get, estress(i,4), ETAB, 4, ELEM, enum(i) \n')
    fh.write('*get, estress(i,5), ETAB, 5, ELEM, enum(i) \n')
    fh.write('*get, estress(i,6), ETAB, 6, ELEM, enum(i) \n')
    fh.write('*get, estress(i,7), ETAB, 7, ELEM, enum(i) \n')
    fh.write('*get, estress(i,8), ETAB, 8, ELEM, enum(i) \n')
    fh.write('*get, estress(i,9), ETAB, 9, ELEM, enum(i) \n')
    fh.write('*get, estress(i,10), ETAB, 10, ELEM, enum(i) \n')
    fh.write('*get, estress(i,11), ETAB, 11, ELEM, enum(i) \n')
    fh.write('*get, estress(i,12), ETAB, 12, ELEM, enum(i) \n')
    fh.write('*get, estress(i,13), ETAB, 13, ELEM, enum(i) \n')
    fh.write('*get, estress(i,14), ETAB, 14, ELEM, enum(i) \n')
    fh.write('*Enddo \n')

    fname = str(step_name) + '_' + 'shell_stresses'
    fh.write('*cfopen,' + out_path + '/' + fname + ',txt \n')
    fh.write('*CFWRITE, stresses, E number, Sm11, Sm22, Sm12, Sb11, Sb22, Sb12, Sv11Top, Sv22Top, Sv13Top, Sv11Bot, Sv22Bot, Sv12Bot, St13, St23 \n')
    fh.write('*do,i,1,nelem \n')
    fh.write('*CFWRITE, stresses, enum(i,1), estress(i,1), estress(i,2),estress(i,3), estress(i,4),')
    fh.write('estress(i,5), estress(i,6), estress(i,7), estress(i,8), estress(i,9), estress(i,10),')
    fh.write('estress(i,11), estress(i,12), estress(i,13), estress(i,14) \n')
    fh.write('*Enddo \n')

    fh.write('ESEL, ALL \n')
    fh.write('ETABLE, ERAS \n')
    fh.write('! \n')
    fh.close()

    # fname = str(step_name) + '_' + 'shell_stresses'
    # write_request_write_array(structure, fname, out_path, 'eforces', 6, 4, index_name='enum')
    # write_etable_restart(structure)
