
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas_fea.utilities import postprocess

from compas.viewers import VtkViewer

try:
    from vtk import vtkUnsignedCharArray
except ImportError:
    pass


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
        self.edge_width = 1
        self.structure = structure
        self.nodes = structure.nodes_xyz()
        self.elements = [structure.elements[i].nodes for i in sorted(structure.elements, key=int)]

        self.setup()

        self.add_splitter()

        if structure.steps_order:

            self.add_label(name='label_steps', text='Steps')
            self.add_listbox(name='listbox_steps', items=structure.steps_order, callback=self.update_fields)

            if structure.results.keys():

                self.add_label(name='label_fields_nodal', text='Fields (nodal)')
                self.add_listbox(name='listbox_fields_nodal', items=[], callback=self.nodal_plot)

                self.add_label(name='label_fields_element', text='Fields (element)')
                self.add_listbox(name='listbox_fields_element', items=[], callback=self.element_plot)


    def update_fields(self):

        step = self.listboxes['listbox_steps'].currentText()

        self.listboxes['listbox_fields_nodal'].clear()
        self.listboxes['listbox_fields_element'].clear()

        try:
            keys = list(self.structure.results[step].keys())

            if 'nodal' in keys:
                node_fields = sorted(list(self.structure.results[step]['nodal'].keys()))
                self.listboxes['listbox_fields_nodal'].addItems(node_fields)

            if 'element' in keys:
                element_fields = sorted(list(self.structure.results[step]['element'].keys()))
                self.listboxes['listbox_fields_element'].addItems(element_fields)

        except:
            pass


    def nodal_plot(self):

        try:
            step  = self.listboxes['listbox_steps'].currentText()
            field = self.listboxes['listbox_fields_nodal'].currentText()

            mode = ''
            scale = 1
            cbar = [None, None]

            nodal_data = self.structure.results[step]['nodal']
            nkeys = sorted(self.structure.nodes, key=int)
            ux = [nodal_data['ux{0}'.format(mode)][i] for i in nkeys]
            uy = [nodal_data['uy{0}'.format(mode)][i] for i in nkeys]
            uz = [nodal_data['uz{0}'.format(mode)][i] for i in nkeys]

            data = [nodal_data['{0}{1}'.format(field, mode)][i] for i in nkeys]
            dtype = 'nodal'

            result = postprocess(self.nodes, self.elements, ux, uy, uz, data, dtype, scale, cbar, 255, None, None)
            toc, U, cnodes, fabs, fscaled, _, _ = result

            self.vertex_colors = vtkUnsignedCharArray()
            self.vertex_colors.SetNumberOfComponents(3)
            for colour in cnodes:
                self.vertex_colors.InsertNextTypedTuple([int(round(i)) for i in colour])
            self.polydata.GetPointData().SetScalars(self.vertex_colors)
            self.main.window.Render()

            print('\n***** Data processed : {0:.3f} s *****'.format(toc))

        except:
            print('\n***** Error encountered during data processing or plotting *****')


    def element_plot(self):

        print('Not Implemented')


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    from compas_fea.structure import Structure

    fnm = '/home/al/temp/knit_candela.obj'

    mdl = Structure.load_from_obj(fnm)
    mdl.view()
