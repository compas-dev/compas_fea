
# from __future__ import absolute_import
# from __future__ import division
# from __future__ import print_function


# Author(s): Andrew Liew (github.com/andrewliew)


# __all__ = [
#     'write_input_misc',
# ]


# comments = {
#     'abaqus':   '**',
#     'opensees': '#',
#     'sofistik': '$',
#     'ansys':    '!',
# }


# def write_input_misc(f, software, miscs):

#     """ Writes Misc data objects to the input file.

#     Parameters
#     ----------
#     f : obj
#         The open file object for the input file.
#     software : str
#         Analysis software or library to use, 'abaqus', 'opensees', 'sofistik' or 'ansys'.
#     miscs : dict
#         Misc objects from structure.misc.

#     Returns
#     -------
#     None

#     """

#     c = comments[software]

#     f.write('{0} -----------------------------------------------------------------------------\n'.format(c))
#     f.write('{0} ------------------------------------------------------------------------ Misc\n'.format(c))
#     f.write('{0}\n'.format(c))

#     for key, misc in miscs.items():

#         mtype = misc.__name__

#         # Amplitude

#         if mtype == 'Amplitude':

#             if software == 'abaqus':

#                 f.write('*AMPLITUDE, NAME={0}\n'.format(key))
#                 f.write('**\n')

#                 for i, j in misc.values:
#                     f.write('{0}, {1}\n'.format(i, j))

#             elif software == 'opensees':

#                 pass

#             elif software == 'sofistik':

#                 pass

#             elif software == 'ansys':

#                 pass

#         f.write('{0}\n'.format(c))

#     f.write('{0}\n'.format(c))
