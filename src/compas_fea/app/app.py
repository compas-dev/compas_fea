
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.viewers import VtkViewer


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'App',
]


class App(VtkViewer):

    def __init__(self, structure, name='compas_fea App', width=1500, height=1000, data={}):

        data = {}
        data['vertices'] = {i: structure.node_xyz(i) for i in structure.nodes}
        data['edges'] = []
        data['faces'] = {}
        data['fixed'] = []

        try:
            for key in structure.steps[structure.steps_order[0]].displacements:
                displacement = structure.displacements[key]
                nodes = structure.sets[displacement.nodes]['selection']
                data['fixed'].extend(nodes)
        except:
            pass

        for ekey, element in structure.elements.items():
            nodes = element.nodes

            if len(nodes) == 2:
                sp, ep = nodes
                if element.__name__ == 'TrussElement':
                    col = [255, 150, 150]
                elif element.__name__ == 'BeamElement':
                    col = [150, 150, 255]
                elif element.__name__ == 'SpringElement':
                    col = [200, 255, 0]
                data['edges'].append({'u': sp, 'v': ep, 'color': col})

            elif (len(nodes) == 3) or (len(nodes) == 4):
                data['faces'][ekey] = {'vertices': nodes, 'color': [150, 250, 150]}

        VtkViewer.__init__(self, name=name, width=width, height=height, data=data)


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":

    from compas_fea.structure import Structure

    fnm = '/home/al/temp/roof.obj'
    # fnm = '/home/al/temp/mesh_floor.obj'

    mdl = Structure.load_from_obj(fnm)
    mdl.view()
