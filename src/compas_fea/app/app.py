
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas_fea.utilities import postprocess

from compas.viewers import VtkViewer

from numpy import array
from numpy import hstack
from numpy import newaxis
from numpy import zeros


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
        data['edges']    = []
        data['faces']    = {}
        data['fixed']    = set()

        try:
            for key in structure.steps[structure.steps_order[0]].displacements:
                displacement = structure.displacements[key]
                nodes = structure.sets[displacement.nodes]['selection']
                data['fixed'] |= set(nodes)
            data['fixed'] = list(data['fixed'])
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


        VtkViewer.__init__(self, name=name, data=data, width=width, height=height)

        xb, yb, zb = structure.node_bounds()
        xm = 0.5 * (xb[0] + xb[1])
        ym = 0.5 * (yb[0] + yb[1])
        zm = 0.5 * (zb[0] + zb[1])

        self.camera_target = [xm, ym, zm]
        self.vertex_size = 1
        self.edge_width = 0
        self.structure = structure
        self.nodes = structure.nodes_xyz()
        self.nkeys = sorted(structure.nodes, key=int)
        self.xyz = array(self.nodes)
        self.U = zeros(self.xyz.shape)
        self.elements = [structure.elements[i].nodes for i in sorted(structure.elements, key=int)]

        self.setup()

        self.add_label(name='label_scale', text='Scale: {0}'.format(1))
        self.add_slider(name='slider_scale', value=1, minimum=0, maximum=1000, interval=100,
                        callback=self.scale_callback)

        if structure.steps_order:

            self.add_label(name='label_steps', text='Steps')
            self.add_listbox(name='listbox_steps', items=structure.steps_order, callback=self.update_fields)

            if structure.results.keys():

                self.add_label(name='label_fields_nodal', text='Fields (nodal)')
                self.add_listbox(name='listbox_fields_nodal', items=[], callback=self.nodal_plot)

                self.add_label(name='label_fields_element', text='Fields (element)')
                self.add_listbox(name='listbox_fields_element', items=[], callback=self.element_plot)


    def scale_callback(self):

        value = self.sliders['slider_scale'].value()
        X = self.xyz + self.U * value
        self.labels['label_scale'].setText('Scale: {0}'.format(value))
        self.update_vertices_coordinates({i: X[i, :] for i in range(X.shape[0])})


    def update_fields(self):

        step = self.listboxes['listbox_steps'].currentText()

        self.listboxes['listbox_fields_nodal'].clear()
        self.listboxes['listbox_fields_element'].clear()

        try:
            keys = list(self.structure.results[step].keys())

            if 'nodal' in keys:

                node_fields = sorted(list(self.structure.results[step]['nodal'].keys()))
                self.listboxes['listbox_fields_nodal'].addItems(node_fields)

                mode = ''
                nodal_data = self.structure.results[step]['nodal']
                self.ux = [nodal_data['ux{0}'.format(mode)][i] for i in self.nkeys]
                self.uy = [nodal_data['uy{0}'.format(mode)][i] for i in self.nkeys]
                self.uz = [nodal_data['uz{0}'.format(mode)][i] for i in self.nkeys]
                self.U = hstack([array(self.ux)[:, newaxis], array(self.uy)[:, newaxis], array(self.uz)[:, newaxis]])

            if 'element' in keys:

                element_fields = sorted(list(self.structure.results[step]['element'].keys()))
                self.listboxes['listbox_fields_element'].addItems(element_fields)

        except:
            pass


    def nodal_plot(self):

        try:
            step  = self.listboxes['listbox_steps'].currentText()
            field = self.listboxes['listbox_fields_nodal'].currentText()

            cbar = [None, None]

            nodal_data = self.structure.results[step]['nodal']
            data = [nodal_data['{0}{1}'.format(field, '')][i] for i in self.nkeys]
            dtype = 'nodal'

            result = postprocess(self.nodes, self.elements, self.ux, self.uy, self.uz, data, dtype, 1, cbar, 255,
                                 None, None)
            toc, _, cnodes, fabs, fscaled, _, _ = result

            self.update_vertices_colors({i: j for i, j in enumerate(cnodes)})

            print('\n***** Data processed : {0:.3f} s *****'.format(toc))

        except:
            pass


    def element_plot(self):

        try:
            step  = self.listboxes['listbox_steps'].currentText()
            field = self.listboxes['listbox_fields_element'].currentText()

            if field != 'axes':

                iptype = 'mean'
                nodal  = 'mean'

                cbar = [None, None]

                data = self.structure.results[step]['element'][field]
                dtype = 'element'

                result = postprocess(self.nodes, self.elements, self.ux, self.uy, self.uz, data, dtype, 1, cbar, 255,
                                     iptype, nodal)
                toc, _, cnodes, fabs, fscaled, _, _ = result

                self.update_vertices_colors({i: j for i, j in enumerate(cnodes)})

            print('\n***** Data processed : {0:.3f} s *****'.format(toc))

        except:
            pass


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":


    from compas_fea.structure import Structure

    fnm = '/home/al/temp/knit_candela.obj'

    mdl = Structure.load_from_obj(fnm)
    mdl.view()
