
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas_fea.utilities import postprocess

from compas.viewers.vtkviewer import VtkViewer

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

    def __init__(self, structure, name='compas_fea App', width=1500, height=1000, data={}, mode=''):

        data = {}
        data['vertices'] = structure.nodes_xyz()
        data['edges']    = []
        data['faces']    = []

        for ekey, element in structure.elements.items():

            nodes = element.nodes

            # Beams, trussea and springs

            if len(nodes) == 2:

                if element.__name__ == 'TrussElement':
                    col = [255, 150, 150]

                elif element.__name__ == 'BeamElement':
                    col = [150, 150, 255]

                elif element.__name__ == 'SpringElement':
                    col = [200, 255, 0]

                data['edges'].append({'vertices': nodes, 'color': col})

            # Tris and quads

            elif (len(nodes) == 3) or (len(nodes) == 4):

                data['faces'].append({'vertices': nodes, 'color': [150, 250, 150]})


        VtkViewer.__init__(self, name=name, data=data, width=width, height=height)

        xb, yb, zb = structure.node_bounds()
        xm = 0.5 * (xb[0] + xb[1])
        ym = 0.5 * (yb[0] + yb[1])
        zm = 0.5 * (zb[0] + zb[1])

        self.camera_target = [xm, ym, zm]
        self.vertex_size   = 1
        self.edge_width    = 10
        self.structure     = structure
        self.nodes         = structure.nodes_xyz()
        self.nkeys         = sorted(structure.nodes, key=int)
        self.elements      = [structure.elements[i].nodes for i in sorted(structure.elements, key=int)]
        self.mode          = mode

        self.xyz = array(self.nodes)
        self.U   = zeros(self.xyz.shape)

        # UI setup

        self.setup()

        self.add_label(name='scale', text='Scale: {0}'.format(1))
        self.add_slider(name='scale', value=1, min=0, max=1000, interval=100, callback=self.scale_callback)

        if structure.steps_order:

            self.add_label(name='steps', text='Steps')
            self.add_listbox(name='steps', items=structure.steps_order, callback=self.update_fields)

            if structure.results.keys():

                self.add_label(name='fields_nodal', text='Fields (nodal)')
                self.add_listbox(name='fields_nodal', items=[], callback=self.nodal_plot)

                self.add_label(name='fields_element', text='Fields (element)')
                self.add_listbox(name='fields_element', items=[], callback=self.element_plot)

                self.add_label(name='iptype', text='iptype')
                self.add_listbox(name='iptype', items=['mean', 'min', 'max'], callback=self.element_plot)

                self.add_label(name='nodal', text='nodal')
                self.add_listbox(name='nodal', items=['mean', 'min', 'max'], callback=self.element_plot)


    def scale_callback(self):

        value = self.sliders['scale'].value()
        X     = self.xyz + self.U * value

        self.labels['scale'].setText('Scale: {0}'.format(value))
        self.update_vertices_coordinates({i: X[i, :] for i in range(self.structure.node_count())})


    def update_fields(self):

        self.listboxes['fields_nodal'].clear()
        self.listboxes['fields_element'].clear()
        step = self.listboxes['steps'].currentText()

        try:

            keys    = list(self.structure.results[step].keys())
            results = self.structure.results[step]

            if 'nodal' in keys:

                node_fields = sorted(list(results['nodal'].keys()))
                self.listboxes['fields_nodal'].addItems(['-select-'] + node_fields)

                mode = self.mode
                self.ux = array([results['nodal']['ux{0}'.format(mode)][i] for i in self.nkeys])
                self.uy = array([results['nodal']['uy{0}'.format(mode)][i] for i in self.nkeys])
                self.uz = array([results['nodal']['uz{0}'.format(mode)][i] for i in self.nkeys])
                self.U  = hstack([self.ux[:, newaxis], self.uy[:, newaxis], self.uz[:, newaxis]])

            if 'element' in keys:

                element_fields = sorted(list(results['element'].keys()))
                self.listboxes['fields_element'].addItems(['-select-'] + element_fields)

            self.scale_callback()

        except:

            pass


    def nodal_plot(self):

        try:

            step  = self.listboxes['steps'].currentText()
            field = self.listboxes['fields_nodal'].currentText()

            cbar = [None, None]
            data = [self.structure.results[step]['nodal']['{0}{1}'.format(field, self.mode)][i] for i in self.nkeys]

            result = postprocess(self.nodes, self.elements, self.ux, self.uy, self.uz, data, 'nodal', 1, cbar,
                                 255, None, None)
            toc, _, cnodes, *_ = result

            self.update_vertices_colors({i: j for i, j in enumerate(cnodes)})
            self.update_statusbar('Plotting: {0:.3f} s'.format(toc))

        except:

            pass


    def element_plot(self):

        try:

            step  = self.listboxes['steps'].currentText()
            field = self.listboxes['fields_element'].currentText()

            if field != 'axes':

                iptype = self.listboxes['iptype'].currentText()
                nodal  = self.listboxes['nodal'].currentText()
                cbar   = [None, None]
                data   = self.structure.results[step]['element'][field]

                result = postprocess(self.nodes, self.elements, self.ux, self.uy, self.uz, data, 'element', 1, cbar,
                                     255, iptype, nodal)
                toc, _, cnodes, *_ = result

                self.update_vertices_colors({i: j for i, j in enumerate(cnodes)})
                self.update_statusbar('Plotting: {0:.3f} s'.format(toc))

        except:

            pass


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    from compas_fea.structure import Structure

    fnm = '/home/al/temp/example_shell.obj'

    mdl = Structure.load_from_obj(fnm)
    mdl.view()
