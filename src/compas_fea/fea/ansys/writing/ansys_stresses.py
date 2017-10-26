__author__     = ['Tomas Mendez Echenagucia <mendez@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'mendez@arch.ethz.ch'


def write_request_nodal_stresses(path, name, step_name):
    out_path = path + '/' + name + '_output/'
    filename = name + '_extract.txt'
    fname = str(step_name) + '_' + 'nodal_stresses'
    name = 'nds_s'

    cFile = open(path + "/" + filename, 'a')
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
    cFile.write('*cfopen,' + out_path + fname + ',txt \n')
    cFile.write('*vwrite, ' + name + '(1) , \',\'  , SXtop(1) ,   \',\' ,   SYtop(1) ')
    cFile.write(',   \',\' ,  SZtop(1) , \',\',    SXbot(1) ,   \',\' ,   SYbot(1) ,   \',\' ,  SZbot(1) \n')
    cFile.write('(F.8, A, ES, A, ES, A, ES, A, ES, A, ES, A, ES) \n')
    cFile.write('*cfclose \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_request_pricipal_stresses(path, name, step_name):
    out_path = path + '/' + name + '_output/'
    filename = name + '_extract.txt'
    fname = str(step_name) + '_' + 'principal_stresses'
    name = 'nds_p'
    cFile = open(path + "/" + filename, 'a')
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
    cFile.write('*cfopen,' + out_path + fname + ',txt \n')
    cFile.write('*vwrite, ' + name + '(1), \',\', S1top(1), \',\', S2top(1), \',\',')
    cFile.write(' S3top(1), \',\', S1bot(1), \',\', S2bot(1), \',\', S3bot(1) \n')
    cFile.write('(F.8, A, ES, A, ES, A, ES, A, ES, A, ES, A, ES) \n')
    cFile.write('*cfclose \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_request_shear_stresses(path, name, step_name):
    out_path = path + '/' + name + '_output/'
    filename = name + '_extract.txt'
    fname = str(step_name) + '_' + 'shear_stresses'
    name = 'nds_sh'

    cFile = open(path + "/" + filename, 'a')
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
    cFile.write('*cfopen,' + out_path + fname + ',txt \n')
    cFile.write('*vwrite, ' + name + '(1), \',\', S1top(1), \',\', S2top(1), \',\',')
    cFile.write(' S3top(1), \',\', S1bot(1), \',\', S2bot(1), \',\', S3bot(1) \n')
    cFile.write('(F.8, A, ES, A, ES, A, ES, A, ES , A, ES, A, ES) \n')
    cFile.write('*cfclose \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_request_principal_strains(path, name, step_name):
    out_path = path + '/' + name + '_output/'
    filename = name + '_extract.txt'
    fname = str(step_name) + '_' + 'principal_strains'
    name = 'nds_ps'

    cFile = open(path + "/" + filename, 'a')
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
    cFile.write('*cfopen,' + out_path + fname + ',txt \n')
    cFile.write('*vwrite,' + name + '(1), \',\', S1top(1), \',\', S2top(1), \',\',')
    cFile.write(' S3top(1), \',\', S1bot(1), \',\', S2bot(1), \',\', S3bot(1) \n')
    cFile.write('(F.8, A, ES, A, ES, A, ES, A, ES, A, ES, A, ES) \n')
    cFile.write('*cfclose \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_request_reactions(path, name, step_name):
    out_path = path + '/' + name + '_output/'
    filename = name + '_extract.txt'
    fname = str(step_name) + '_' + 'reactions'
    name = 'nds_r'

    cFile = open(path + "/" + filename, 'a')
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
    cFile.write('*cfopen,' + out_path + fname + ',txt \n')
    cFile.write('*vwrite, ' + name + '(1), \',\', RFX(1), \',\', RFY(1), \',\', ')
    cFile.write('RFZ(1), \',\', RMX(1), \',\', RMY(1), \',\', RMZ(1) \n')
    cFile.write('(F.8, A, ES, A, ES, A, ES, A, ES, A, ES, A, ES) \n')
    cFile.write('*cfclose \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()
