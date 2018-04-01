# def input_write_misc(f, misc):

#     """ Writes misc class info to the Abaqus .inp file.

#     Parameters
#     ----------
#     f : obj
#         The open file object for the .inp file.
#     misc : dic
#         Misc objects from structure.misc.

#     Returns
#     -------
#     None

#     """

#     f.write('** -----------------------------------------------------------------------------\n')
#     f.write('** ------------------------------------------------------------------------ Misc\n')
#     f.write('**\n')

#     for key, misc in misc.items():

#         mtype = misc.__name__

#         if mtype in ['Amplitude']:

#             f.write('** {0}\n'.format(key))
#             f.write('** ' + '-' * len(key) + '\n')
#             f.write('**\n')

#         # Amplitude

#         if mtype == 'Amplitude':

#             f.write('*AMPLITUDE, NAME={0}\n'.format(key))
#             f.write('**\n')
#             for i, j in misc.values:
#                 f.write('{0}, {1}\n'.format(i, j))

#         f.write('**\n')
