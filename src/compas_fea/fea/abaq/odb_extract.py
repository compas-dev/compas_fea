
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

try:
    from job import *
except:
    pass

import json
import sys


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'extract_odb_data'
]


conversion = {
    'U1': 'ux', 'U2': 'uy', 'U3': 'uz',
    'UR1': 'urx', 'UR2': 'ury', 'UR3': 'urz',
    'RF1': 'rfx', 'RF2': 'rfy', 'RF3': 'rfz',
    'RM1': 'rmx', 'RM2': 'rmy', 'RM3': 'rmz',
    'S11': 'sxx', 'S22': 'syy', 'S33': 'szz', 'S12': 'sxy', 'S13': 'sxz', 'S23': 'sxz',
    'E11': 'exx', 'E22': 'eyy', 'E33': 'ezz', 'E12': 'exy', 'E13': 'exz', 'E23': 'exz',
    'LE11': 'exx', 'LE22': 'eyy', 'LE33': 'ezz', 'LE12': 'exy', 'LE13': 'exz', 'LE23': 'exz',
    'PE11': 'pexx', 'PE22': 'peyy', 'PE33': 'pezz', 'PE12': 'pexy', 'PE13': 'pexz', 'PE23': 'pexz',
    'SF1': 'sfnx', 'SF2': 'sfvy', 'SF3': 'sfvx',
    'SM1': 'smx', 'SM2': 'smy', 'SM3': 'smz',
    'SK1': 'skx', 'SK2': 'sky', 'SK3': 'skz',
    'SE1': 'senx', 'SE2': 'sevy', 'SE3': 'sevx',
    'CTF1': 'spfx', 'CTF2': 'spfy', 'CTF3': 'spfz',
    'VALUE': 'rbfor',
}

node_fields = ['rf', 'rm', 'u', 'ur', 'cf', 'cm']
element_fields = ['sf', 'sm', 'sk', 'se', 's', 'e', 'pe', 'spf', 'rbfor']


def extract_odb_data(temp, name, fields, steps='all'):

    """ Extracts data from the .odb file for requested steps.

    Parameters
    ----------
    temp : str
        Folder containing the analysis .odb file.
    name : str
        Name of the Structure object and analysis files.
    fields : list
        Data field requests.
    steps : list
        tr): Steps to extract data for, 'all' for all steps.

    Returns
    -------
    None

    """

    odb = openOdb(path='{0}{1}.odb'.format(temp, name))

    results = {}

    if steps == 'all':
        steps = list(odb.steps.keys())

    for step in steps:

        results[step] = {}
        frame = odb.steps[step].frames[-1]
        # description = frame.description
        fieldoutputs = frame.fieldOutputs

        # Node data

        results[step]['nodal'] = {}

        for field in node_fields:
            if field in fields.split(','):

                clabels = list(fieldoutputs[field.upper()].componentLabels)
                ref = results[step]['nodal']
                for c in clabels:
                    ref[conversion[c]] = {}
                ref[field + 'm'] = {}

                for value in fieldoutputs[field.upper()].values:
                    data = value.data
                    if isinstance(data, float):
                        data = [data]
                    node = value.nodeLabel - 1

                    for i, c in enumerate(clabels):
                        ref[conversion[c]][node] = float(data[i])
                    ref[field + 'm'][node] = float(value.magnitude)

        # Element data

        results[step]['element'] = {}

        for field in element_fields:
            if field in fields.split(','):

                ref = results[step]['element']

                if field == 'spf':
                    field = 'ctf'
                if field == 'e':
                    field = 'le'

                if field == 'rbfor':
                    clabels = ['VALUE']
                else:
                    clabels = list(fieldoutputs[field.upper()].componentLabels)

                for c in clabels:
                    ref[conversion[c]] = {}

                if field == 's':
                    ref['smises'] = {}

                if field in ['s', 'e', 'pe']:
                    ref[field + 'maxp'] = {}
                    ref[field + 'minp'] = {}
                elif field == 'le':
                    ref['emaxp'] = {}
                    ref['eminp'] = {}

                for value in fieldoutputs[field.upper()].values:
                    data = value.data
                    if isinstance(data, float):
                        data = [data]
                    element = value.elementLabel - 1
                    ip = value.integrationPoint
                    sp = value.sectionPoint.number if value.sectionPoint else 0
                    id = 'ip{0}_sp{1}'.format(ip, sp)

                    for i, c in enumerate(clabels):
                        try:
                            for i, c in enumerate(clabels):
                                ref[conversion[c]][element][id] = float(data[i])
                        except:
                            ref[conversion[c]][element] = {}
                            try:
                                ref[conversion[c]][element][id] = float(data[i])
                            except:
                                ref[conversion[c]][element][id] = None

                    if field == 's':
                        try:
                            ref['smises'][element][id] = float(value.mises)
                        except:
                            ref['smises'][element] = {}
                            try:
                                ref['smises'][element][id] = float(value.mises)
                            except:
                                ref['smises'][element][id] = None

                    if field in ['s', 'e', 'pe']:
                        try:
                            ref[field + 'maxp'][element][id] = float(value.maxPrincipal)
                            ref[field + 'minp'][element][id] = float(value.minPrincipal)
                        except:
                            ref[field + 'maxp'][element] = {}
                            ref[field + 'minp'][element] = {}
                            try:
                                ref[field + 'maxp'][element][id] = float(value.maxPrincipal)
                                ref[field + 'minp'][element][id] = float(value.minPrincipal)
                            except:
                                ref[field + 'maxp'][element][id] = None
                                ref[field + 'minp'][element][id] = None

                    if field == 'le':  # temp fix
                        try:
                            ref['emaxp'][element][id] = float(value.maxPrincipal)
                            ref['eminp'][element][id] = float(value.minPrincipal)
                        except:
                            ref['emaxp'][element] = {}
                            ref['eminp'][element] = {}
                            try:
                                ref['emaxp'][element][id] = float(value.maxPrincipal)
                                ref['eminp'][element][id] = float(value.minPrincipal)
                            except:
                                ref['emaxp'][element][id] = None
                                ref['eminp'][element][id] = None

                    # if field is not 'RBFOR':
                        # dic['axes'][element][id] = value.localCoordSystem

    with open('{0}{1}-results.json'.format(temp, name), 'w') as f:
        json.dump(results, f)


if __name__ == "__main__":

    temp = sys.argv[-1]
    name = sys.argv[-2]
    fields = sys.argv[-3]

    extract_odb_data(temp=temp, name=name, fields=fields)
