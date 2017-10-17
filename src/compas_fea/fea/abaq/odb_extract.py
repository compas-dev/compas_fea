"""
Abaqus .odb data extraction file and function.
"""

from __future__ import print_function
from __future__ import absolute_import

try:
    from job import *
except:
    pass

import json
import sys


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


__all__ = [
    'extract_odb_data'
]


node_fields = ['RF', 'RM', 'U', 'UR', 'CF', 'CM', 'NT']
element_fields = ['SF', 'SM', 'SE', 'SK', 'S', 'E', 'PE', 'RBFOR']


def extract_odb_data(temp, name, fields, steps='all'):
    """ Extracts data from the .odb file for requested steps.

    Parameters:
        temp (str): Folder containing the analysis .odb file.
        name (str): Name of the Structure object and analysis files.
        fields (str): Fields to extract e.g 'U,S,CF'.
        steps (list, str): Steps to extract data for, 'all' for all steps.

    Returns:
        None
    """
    odb = openOdb(path='{0}{1}.odb'.format(temp, name))

    results = {}

    fields = fields.split(',')
    if steps == 'all':
        steps = list(odb.steps.keys())

    for step in steps:
        results[step] = {}
        frame = odb.steps[step].frames[-1]
        description = frame.description
        fieldoutputs = frame.fieldOutputs

        # Node data

        for field in node_fields:
            if field in fields:
                clabels = list(fieldoutputs[field].componentLabels)
                call = clabels + ['magnitude']
                dic = {c: {} for c in call}

                for value in fieldoutputs[field].values:
                    data = value.data
                    if isinstance(data, float):
                        data = [data]
                    node = value.nodeLabel - 1
                    for i, c in enumerate(clabels):
                        dic[c][node] = float(data[i])
                    dic['magnitude'][node] = float(value.magnitude)

                with open('{0}{1}-{2}-{3}.json'.format(temp, name, step, field), 'w') as f:
                    json.dump(dic, f)
                results[step][field] = dic

        # Element data

        for field in element_fields:
            if field in fields:
                clabels = list(fieldoutputs[field].componentLabels)
                if clabels:
                    call = clabels + ['mises', 'maxPrincipal', 'minPrincipal', 'axes']
                else:
                    call, clabels = ['VALUE'], ['VALUE']
                dic = {c: {} for c in call}

                for value in fieldoutputs[field].values:
                    data = value.data
                    if isinstance(data, float):
                        data = [data]
                    element = value.elementLabel - 1
                    ip = value.integrationPoint
                    sp = value.sectionPoint.number if value.sectionPoint else 0
                    id = 'ip{0}_sp{1}'.format(ip, sp)
                    for i, c in enumerate(clabels):
                        try:
                            dic[c][element][id] = float(data[i])
                        except:
                            for j in call:
                                dic[j][element] = {}
                                try:
                                    dic[c][element][id] = float(data[i])
                                except:
                                    pass
                    if field is not 'RBFOR':
                        dic['mises'][element][id] = float(value.mises) if value.mises else None
                        dic['maxPrincipal'][element][id] = float(value.maxPrincipal) if value.maxPrincipal else None
                        dic['minPrincipal'][element][id] = float(value.minPrincipal) if value.minPrincipal else None
                        dic['axes'][element][id] = value.localCoordSystem

                with open('{0}{1}-{2}-{3}.json'.format(temp, name, step, field), 'w') as f:
                    json.dump(dic, f)
                results[step][field] = dic

        info_dic = {'description': description}
        with open('{0}{1}-{2}-info.json'.format(temp, name, step), 'w') as f:
            json.dump(info_dic, f)

    with open('{0}{1}-results.json'.format(temp, name), 'w') as f:
        json.dump(results, f)


if __name__ == "__main__":

    temp = sys.argv[-1]
    name = sys.argv[-2]
    fields = sys.argv[-3]

    extract_odb_data(temp=temp, name=name, fields=fields)
