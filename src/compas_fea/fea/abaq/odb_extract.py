from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

try:
    from job import openOdb
except ImportError:
    pass

import json
import sys


# Author(s): Andrew Liew (github.com/andrewliew)


__all__ = [
    'extract_odb_data'
]


convert = {
    'CF1':   'cfx',  'CF2':  'cfy',  'CF3':  'cfz', 'CFM': 'cfm',
    'CM1':   'cmx',  'CM2':  'cmy',  'CM3':  'cmz', 'CMM': 'cmm',
    'U1':    'ux',   'U2':   'uy',   'U3':   'uz',  'UM':  'um',
    'UR1':   'urx',  'UR2':  'ury',  'UR3':  'urz', 'URM': 'urm',
    'RF1':   'rfx',  'RF2':  'rfy',  'RF3':  'rfz', 'RFM': 'rfm',
    'RM1':   'rmx',  'RM2':  'rmy',  'RM3':  'rmz', 'RMM': 'rmm',
    'S11':   'sxx',  'S22':  'syy',  'S33':  'szz',  'S12':  'sxy',  'S13':  'sxz',  'S23':  'sxz',
    'E11':   'exx',  'E22':  'eyy',  'E33':  'ezz',  'E12':  'exy',  'E13':  'exz',  'E23':  'exz',
    'LE11':  'exx',  'LE22': 'eyy',  'LE33': 'ezz',  'LE12': 'exy',  'LE13': 'exz',  'LE23': 'exz',
    'PE11':  'pexx', 'PE22': 'peyy', 'PE33': 'pezz', 'PE12': 'pexy', 'PE13': 'pexz', 'PE23': 'pexz',
    'SF1':   'sf1',  'SF2':  'sf2',  'SF3':  'sf3',  'SF4':  'sf4',  'SF5':  'sf5',  'SF6':  'sf6',
    'SM1':   'sm1',  'SM2':  'sm2',  'SM3':  'sm3',
    'SK1':   'skx',  'SK2':  'sky',  'SK3':  'skz',
    'SE1':   'se1',  'SE2':  'se2',  'SE3':  'se3',
    'CTF1':  'spfx', 'CTF2': 'spfy', 'CTF3': 'spfz',

    'VALUE':  'rbfor',
    'AXES':   'axes',
    'SMISES': 'smises', 'SMAXP': 'smaxp', 'SMINP': 'sminp',
}

node_fields = ['rf', 'rm', 'u', 'ur', 'cf', 'cm']
element_fields = ['sf', 'sm', 'sk', 'se', 's', 'e', 'pe', 'ctf', 'rbfor']


def extract_odb_data(temp, name, fields, components, steps='all'):
    """ Extracts data from the .odb file for the requested steps and fields.

    Parameters
    ----------
    temp : str
        Folder path containing the analysis .odb file.
    name : str
        Name of the Structure object.
    fields : list
        Data field requests.
    components : list
        Specific components to extract from the fields data.
    steps : list, str
        Step names to extract data for, or 'all' for all steps.

    Returns
    -------
    None

    """

    odb = openOdb(path='{0}{1}.odb'.format(temp, name))

    if not components:
        components = set()
        for value in convert.values():
            components.add(value)
    else:
        components = set(components)

    results = {}
    info = {}

    if steps == 'all':
        steps = odb.steps.keys()

    for step in steps:

        results[step] = {'nodal': {}, 'element': {}}
        info[step] = {}

        description = odb.steps[step].frames[-1].description

        refn = results[step]['nodal']
        refe = results[step]['element']

        if 'Mode' in description:

            info[step]['description'] = {}

            counter = 0

            for fi in range(len(odb.steps[step].frames)):

                frame = odb.steps[step].frames[fi]
                fieldoutputs = frame.fieldOutputs
                info[step]['description'][counter] = frame.description

                clabels = list(fieldoutputs['U'].componentLabels)

                for c in clabels:
                    if convert[c] in components:
                        refn[convert[c] + str(counter)] = {}

                if 'um' in components:
                    refn['um' + str(counter)] = {}

                for value in fieldoutputs['U'].values:

                    data = value.data
                    node = value.nodeLabel - 1

                    for i, c in enumerate(clabels):
                        if convert[c] in components:
                            refn[convert[c] + str(counter)][node] = float(data[i])

                    if 'um' in components:
                        refn['um' + str(counter)][node] = float(value.magnitude)

                counter += 1

            try:
                frequencies = odb.steps[step].historyRegions['Assembly Assembly-1'].historyOutputs['EIGFREQ'].data
                results[step]['frequencies'] = [i[1] for i in frequencies]
            except Exception:
                pass

            try:
                masses = odb.steps[step].historyRegions['Assembly Assembly-1'].historyOutputs['GM'].data
                results[step]['masses'] = [i[1] for i in masses]
            except Exception:
                pass

        else:

            info[step]['description'] = description

            frame = odb.steps[step].frames[-1]
            fieldoutputs = frame.fieldOutputs

            # Node data

            for field in node_fields:

                if field in fields:

                    clabels = list(fieldoutputs[field.upper()].componentLabels)

                    for c in clabels:
                        if convert[c] in components:
                            refn[convert[c]] = {}

                    if field + 'm' in components:
                        refn[field + 'm'] = {}

                    for value in fieldoutputs[field.upper()].values:

                        data = value.data
                        if isinstance(data, float):
                            data = [data]
                        node = value.nodeLabel - 1

                        for i, c in enumerate(clabels):
                            if convert[c] in components:
                                refn[convert[c]][node] = float(data[i])

                        if field + 'm' in components:
                            refn[field + 'm'][node] = float(value.magnitude)

            # Element data

            for field in element_fields:

                if field in fields:

                    try:

                        field = 'ctf'if field == 'spf' else field
                        field = 'le' if field == 'e' else field

                        clabels = ['VALUE'] if field == 'rbfor' else list(fieldoutputs[field.upper()].componentLabels)

                        for c in clabels:
                            if convert[c] in components:
                                refe[convert[c]] = {}

                        if (field == 's') and ('smises' in components):
                            refe['smises'] = {}

                        if field in ['s', 'pe']:
                            if field + 'maxp' in components:
                                refe[field + 'maxp'] = {}
                            if field + 'minp' in components:
                                refe[field + 'minp'] = {}
                            if 'axes' in components:
                                refe['axes'] = {}

                        elif field == 'le':
                            if 'emaxp' in components:
                                refe['emaxp'] = {}
                            if 'eminp' in components:
                                refe['eminp'] = {}

                        for value in fieldoutputs[field.upper()].values:

                            data = value.data
                            if isinstance(data, float):
                                data = [data]

                            element = value.elementLabel - 1
                            ip = value.integrationPoint
                            sp = value.sectionPoint.number if value.sectionPoint else 0
                            id = 'ip{0}_sp{1}'.format(ip, sp)

                            for i, c in enumerate(clabels):
                                if convert[c] in components:
                                    try:
                                        refe[convert[c]][element][id] = float(data[i])
                                    except Exception:
                                        refe[convert[c]][element] = {}
                                        try:
                                            refe[convert[c]][element][id] = float(data[i])
                                        except Exception:
                                            refe[convert[c]][element][id] = None

                            if field == 's':
                                if 'smises' in components:
                                    try:
                                        refe['smises'][element][id] = float(value.mises)
                                    except Exception:
                                        refe['smises'][element] = {}
                                        try:
                                            refe['smises'][element][id] = float(value.mises)
                                        except Exception:
                                            refe['smises'][element][id] = None

                            if field in ['s', 'pe']:
                                try:
                                    if field + 'maxp' in components:
                                        refe[field + 'maxp'][element][id] = float(value.maxPrincipal)
                                    if field + 'minp' in components:
                                        refe[field + 'minp'][element][id] = float(value.minPrincipal)
                                    if 'axes' in components:
                                        refe['axes'][element] = value.localCoordSystem
                                except Exception:
                                    refe[field + 'maxp'][element] = {}
                                    refe[field + 'minp'][element] = {}
                                    try:
                                        if field + 'maxp' in components:
                                            refe[field + 'maxp'][element][id] = float(value.maxPrincipal)
                                        if field + 'minp' in components:
                                            refe[field + 'minp'][element][id] = float(value.minPrincipal)
                                    except Exception:
                                        if field + 'maxp' in components:
                                            refe[field + 'maxp'][element][id] = None
                                        if field + 'minp' in components:
                                            refe[field + 'minp'][element][id] = None

                            if field == 'le':
                                try:
                                    if 'emaxp' in components:
                                        refe['emaxp'][element][id] = float(value.maxPrincipal)
                                    if 'eminp' in components:
                                        refe['eminp'][element][id] = float(value.minPrincipal)
                                except Exception:
                                    refe['emaxp'][element] = {}
                                    refe['eminp'][element] = {}
                                    try:
                                        if 'emaxp' in components:
                                            refe['emaxp'][element][id] = float(value.maxPrincipal)
                                        if 'eminp' in components:
                                            refe['eminp'][element][id] = float(value.minPrincipal)
                                    except Exception:
                                        if 'emaxp' in components:
                                            refe['emaxp'][element][id] = None
                                        if 'eminp' in components:
                                            refe['eminp'][element][id] = None
                    except Exception:
                        pass

    with open('{0}{1}-results.json'.format(temp, name), 'w') as f:
        json.dump(results, f)

    with open('{0}{1}-info.json'.format(temp, name), 'w') as f:
        json.dump(info, f)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    temp = sys.argv[-1]
    name = sys.argv[-2]
    fields = sys.argv[-3].split(',')
    components = None if sys.argv[-4] == 'None' else sys.argv[-4].split(',')

    extract_odb_data(temp=temp, name=name, fields=fields, components=components)
