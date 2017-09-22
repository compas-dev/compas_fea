"""
compas_fea.structure.structure : The compas_fea main Structure class.
The main datastructure for all structural model information and methods.
"""

from subprocess import Popen
from subprocess import PIPE

from compas.geometry import centroid_points
from compas.utilities import geometric_key

from compas_fea.fea import abaq
from compas_fea.fea.ansys import ansys
from compas_fea.structure.element import *
from compas_fea.structure.step import GeneralStep

import json
import os
import pickle


__author__     = ['Andrew Liew <liew@arch.ethz.ch>', 'Tomas Mendez <mendez@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


__all__ = [
    'Structure',
]


class Structure(object):

    def __init__(self):
        """ Initialises empty Structure object for use in finite element analysis.

        Parameters:
            constraints (dic): Constraint objects.
            displacements (dic): Displacement objects.
            elements (dic): Element objects.
            element_index (dic): Index of elements (geometric keys).
            element_properties (dic): Element properties objects.
            interactions (dic): Interaction objects.
            loads (dic): Load objects.
            materials (dic): Material objects.
            misc (dic): Misc objects.
            nodes (dic): Node co-ordinates and local axes.
            node_index (dic): Index of nodes (geometric keys).
            results (dic): Results from analysis.
            sections (dic): Section objects.
            sets (dic): Node, element and surface sets.
            steps (dic): Step objects.
            tol (str): Geometric key tolerance.

        Returns:
            None
        """
        self.constraints = {}
        self.displacements = {}
        self.elements = {}
        self.element_index = {}
        self.element_properties = {}
        self.interactions = {}
        self.loads = {}
        self.materials = {}
        self.misc = {}
        self.nodes = {}
        self.node_index = {}
        self.results = {}
        self.sections = {}
        self.sets = {}
        self.steps = {}
        self.tol = '3'

# ==============================================================================
# nodes
# ==============================================================================

    def add_node(self, xyz, ex=[1, 0, 0], ey=[0, 1, 0], ez=[0, 0, 1]):
        """ Adds a node to structure.nodes at co-ordinates xyz with local frame [ex, ey, ez].

        Note:
            - Nodes are numbered sequentially starting from 0 (Python based).

        Parameters:
            xyz (list): [x, y, z] co-ordinates of the node.
            ex (list): Node's local x axis.
            ey (list): Node's local y axis.
            ez (list): Node's local z axis.

        Returns:
            int: Key of the added or pre-existing node.
        """
        key = self.check_node_exists(xyz)
        if key is None:
            key = self.node_count()
            self.nodes[key] = {'x': xyz[0], 'y': xyz[1], 'z': xyz[2], 'ex': ex, 'ey': ey, 'ez': ez}
            self.add_node_to_node_index(key, xyz)
        return key

    def add_nodes(self, nodes, ex=[1, 0, 0], ey=[0, 1, 0], ez=[0, 0, 1]):
        """ Adds a list of nodes to structure.nodes at given co-ordinates all with local frame [ex, ey, ez].

        Note:
            - Nodes are numbered sequentially starting from 0 (Python based).

        Parameters:
            nodes (list): [x, y, z] co-ordinates for each node.
            ex (list): Node's local x axis.
            ey (list): Node's local y axis.
            ez (list): Node's local z axis.

        Returns:
            list: Keys of the added or pre-existing nodes.
        """
        return [self.add_node(xyz=node, ex=ex, ey=ey, ez=ez) for node in nodes]

    def add_node_to_node_index(self, key, xyz):
        """ Adds the node to the node_index dictionary.

        Parameters:
            key (int): Prescribed node key.
            xyz (list): [x, y, z] co-ordinates of the node.

        Returns:
            None
        """
        gkey = geometric_key(xyz, '{0}f'.format(self.tol))
        self.node_index[gkey] = key

    def check_node_exists(self, xyz):
        """ Check if a node already exists at given x, y, z co-ordinates.

        Note:
            - Geometric key check is made according to self.tol [m] tolerance.

        Parameters:
            xyz (list): [x, y, z] co-ordinates of node to check.

        Returns:
            int: The node index if the node already exists, None if not.
        """
        gkey = geometric_key(xyz, '{0}f'.format(self.tol))
        return self.node_index.get(gkey, None)

    def make_node_index_dic(self):
        """ Makes a node_index dictionary from existing structure.nodes.

        Parameters:
            None

        Returns:
            None
        """
        for key in list(self.nodes.keys()):
            gkey = geometric_key(self.node_xyz(key), '{0}f'.format(self.tol))
            self.node_index[gkey] = key

    def node_bounds(self):
        """ Return the bounds formed by the Structure's nodal co-ordinates.

        Parameters:
            None

        Returns:
            list: [xmin, xmax].
            list: [ymin, ymax].
            list: [zmin, zmax].
        """
        n = self.node_count()
        x = [0] * n
        y = [0] * n
        z = [0] * n
        for c, node in self.nodes.items():
            x[c] = node['x']
            y[c] = node['y']
            z[c] = node['z']
        xmin, xmax = min(x), max(x)
        ymin, ymax = min(y), max(y)
        zmin, zmax = min(z), max(z)
        return [xmin, xmax], [ymin, ymax], [zmin, zmax]

    def node_count(self):
        """ Return the number of nodes in structure.nodes.

        Parameters:
            None

        Returns:
            int: Number of nodes stored in the Structure object.
        """
        return len(self.nodes)

    def node_xyz(self, node):
        """ Return the xyz co-ordinates of a node.

        Parameters:
            Node (int): Node number.

        Returns:
            list: [x, y, z] co-ordinates.
        """
        return [self.nodes[node][i] for i in 'xyz']

# ==============================================================================
# elements
# ==============================================================================

    def add_element(self, nodes, type, acoustic=False, thermal=False, axes={}):
        """ Adds element to structure.elements with centroid geometric key.

        Note:
            - Elements are numbered sequentially starting from 0 (Python based).

        Parameters:
            nodes (list): Nodes the element is connected to.
            type (str): Element type: 'HexahedronElement', 'BeamElement, 'TrussElement' etc.
            acoustic (bool): Acoustic properties on or off.
            thermal (bool): Thermal properties on or off.
            axes (dic): The local element axes 'ex', 'ey' and 'ez'.

        Returns:
            int: Key of the added or existing element.
        """
        func_dic = {'BeamElement': BeamElement,
                    'TrussElement': TrussElement,
                    'StrutElement': StrutElement,
                    'TieElement': TieElement,
                    'ShellElement': ShellElement,
                    'MembraneElement': MembraneElement,
                    'SolidElement': SolidElement,
                    'TetrahedronElement': TetrahedronElement,
                    'PentahedronElement': PentahedronElement,
                    'HexahedronElement': HexahedronElement}
        func = func_dic[type]
        ekey = self.check_element_exists(nodes)
        if ekey is None:
            ekey = self.element_count()
            element = func()
            element.axes = axes
            element.nodes = nodes
            element.number = ekey
            element.acoustic = acoustic
            element.thermal = thermal
            self.elements[ekey] = element
            self.add_element_to_element_index(ekey, nodes)
        return ekey

    def add_element_to_element_index(self, key, nodes):
        """ Adds the element to the element_index dictionary.

        Parameters:
            key (int): Prescribed element key.
            nodes (list): Node numbers the element is connected to.

        Returns:
            None
        """
        centroid = centroid_points([self.node_xyz(node) for node in nodes])
        gkey = geometric_key(centroid, '{0}f'.format(self.tol))
        self.element_index[gkey] = key

    def check_element_exists(self, nodes=None, xyz=None):
        """ Check if an element already exists based on its centroid.

        Note:
            - Geometric key check is made according to self.tol [m] tolerance.

        Parameters:
            nodes (list) : Node numbers the element is connected to.
            xyz (list): Direct co-ordinates of the element centroid.

        Returns:
            int: The element index if the element already exists, None if not.
        """
        if not xyz:
            xyz = centroid_points([self.node_xyz(node) for node in nodes])
        gkey = geometric_key(xyz, '{0}f'.format(self.tol))
        ekey = self.element_index.get(gkey, None)
        return ekey

    def element_count(self):
        """ Return the number of elements in structure.elements.

        Parameters:
            None

        Returns:
            int: Number of elements stored in the Structure object.
        """
        return len(self.elements)

    def make_element_index_dic(self):
        """ Makes an element_index dictionary from existing structure.elements.

        Parameters:
            None

        Returns:
            None
        """
        for key, element in self.elements.items():
            nodes = element.nodes
            centroid = centroid_points([self.node_xyz(node) for node in nodes])
            gkey = geometric_key(centroid, '{0}f'.format(self.tol))
            self.element_index[gkey] = key

    def element_centroid(self, element):
        """ Return the centroid of an element.

        Parameters:
            element (int): Number of the element.

        Returns:
            list: Co-ordinates of element centroid.
        """
        nodes = self.elements[element].nodes
        return centroid_points([self.node_xyz(node) for node in nodes])


# ==============================================================================
# constructors
# ==============================================================================

    def add_nodes_elements_from_mesh(self, mesh, element_type, acoustic=False, thermal=False):
        """ Adds the nodes and faces of a Mesh to the Structure object.

        Parameters:
            mesh (obj): Mesh datastructure object.
            element_type (str): Element type: 'ShellElement', 'MembraneElement' etc.
            acoustic (bool): Acoustic properties on or off.
            thermal (bool): Thermal properties on or off.

        Returns:
            None: Nodes and elements are updated in the Structure object.
        """
        for key in sorted(list(mesh.vertices()), key=int):
            self.add_node(mesh.vertex_coordinates(key))
        for fkey in list(mesh.faces()):
            face = [self.check_node_exists(mesh.vertex_coordinates(i)) for i in mesh.face[fkey]]
            self.add_element(nodes=face, type=element_type, acoustic=acoustic, thermal=thermal)

    def add_nodes_elements_from_network(self, network, element_type, acoustic=False, thermal=False):
        """ Adds the nodes and edges of a Network to the Structure object.

        Parameters:
            network (obj): Network datastructure object.
            element_type (str): Element type: 'BeamElement', 'TrussElement' etc.
            acoustic (bool): Acoustic properties on or off.
            thermal (bool): Thermal properties on or off.

        Returns:
            None: Nodes and elements are updated in the Structure object.
        """
        for key in sorted(list(network.vertices()), key=int):
            self.add_node(network.vertex_coordinates(key))
        for u, v in list(network.edges()):
            sp = self.check_node_exists(network.vertex_coordinates(u))
            ep = self.check_node_exists(network.vertex_coordinates(v))
            self.add_element(nodes=[sp, ep], type=element_type, acoustic=acoustic, thermal=thermal)

# ==============================================================================
# sets
# ==============================================================================

    def add_set(self, name, type, selection, explode=False):
        """ Adds a node, element or surface set to structure.sets.

        Parameters:
            name (str): Name of the set.
            type (str): 'node', 'element', 'surface_node', surface_element'.
            selection (list): The keys of the nodes, elements or elements and sides.
            explode (bool): Explode the set into sets for each member of selection.

        Returns:
            None
        """
        if explode:
            if type in ['node', 'element']:
                for select in selection:
                    self.sets['{0}_{1}'.format(type, select)] = {'type': type, 'selection': [select], 'explode': False}
        self.sets[name] = {'type': type, 'selection': selection, 'explode': explode}

# ==============================================================================
# modifiers
# ==============================================================================

    def scale_displacements(self, displacements, factor):
        """ Scales displacements by a given factor.

        Parameters:
            displacements (dic): Dictionary containing the displacements to scale.
            factor (float): Factor to scale the displacements by.

        Returns:
            dic: The scaled displacements dictionary.
        """
        disp_dic = {}
        for key, disp in displacements.items():
            for dkey, dcomp in disp.components.items():
                if dcomp is not None:
                    disp.components[dkey] *= factor
            disp_dic[key] = disp
        return disp_dic

    def scale_loads(self, loads, factor):
        """ Scales loads by a given factor.

        Parameters:
            loads (dic): Dictionary containing the loads to scale.
            factor (float): Factor to scale the loads by.

        Returns:
            dic: The scaled loads dictionary.
        """
        loads_dic = {}
        for key, load in loads.items():
            for lkey, lcomp in load.components.items():
                if lcomp is not None:
                    load.components[lkey] *= factor
            loads_dic[key] = load
        return loads_dic

# ==============================================================================
# add objects
# ==============================================================================

    def add_constraint(self, constraint):
        """ Adds a Constraint object to structure.constraints.

        Parameters:
            constraint (obj): The Constraint object.

        Returns:
            None
        """
        constraint.index = len(self.constraints)
        self.constraints[constraint.name] = constraint

    def add_displacement(self, displacement):
        """ Adds a Displacement object to structure.displacements.

        Parameters:
            displacement (obj): The Displacement object.

        Returns:
            None
        """
        displacement.index = len(self.displacements)
        self.displacements[displacement.name] = displacement

    def add_element_properties(self, element_properties, name=None):
        """ Adds an ElementProperties object to structure.element_properties.

        Parameters:
            element_properties (obj): The ElementProperties object.
            name (str): Name for index.

        Returns:
            None
        """
        if name:
            index = name
        else:
            index = len(self.element_properties)
        self.element_properties[index] = element_properties

    def add_interaction(self, interaction):
        """ Adds an Interaction object to structure.interactions.

        Parameters:
            interaction (obj): The Interaction object.

        Returns:
            None
        """
        interaction.index = len(self.interactions)
        self.interactions[interaction.name] = interaction

    def add_load(self, load):
        """ Adds a Load object to structure.loads.

        Parameters:
            load (obj): The Load object.

        Returns:
            None
        """
        load.index = len(self.loads)
        self.loads[load.name] = load

    def add_material(self, material):
        """ Adds a Material object to structure.materials.

        Parameters:
            material (obj): The Material object.

        Returns:
            None
        """
        material.index = len(self.materials)
        self.materials[material.name] = material

    def add_misc(self, misc):
        """ Adds a Misc object to structure.misc.

        Parameters:
            misc (obj): The Misc object.

        Returns:
            None
        """
        misc.index = len(self.misc)
        self.misc[misc.name] = misc

    def add_section(self, section):
        """ Adds a Section object to structure.sections.

        Parameters:
            section (obj): The Section object.

        Returns:
            None
        """
        section.index = len(self.sections)
        self.sections[section.name] = section

    def add_step(self, step):
        """ Adds a Step object to structure.steps.

        Parameters:
            step (obj): The Step object.

        Returns:
            None
        """
        step.index = len(self.steps)
        self.steps[step.name] = step

# ==============================================================================
# steps
# ==============================================================================

    def set_steps_order(self, order):
        """ Sets the order the Steps will be analysed.

        Parameters:
            order: An ordered list of the Step names.

        Returns:
            None
        """
        self.steps['order'] = order

    def combine_static_steps(self):
        """ Combines the static steps in structure.steps.

        Parameters:
            None

        Returns:
            str: The name of the newly created combined Step.
        """
        name = ''
        disp_dic = {}
        loads_dic = {}
        nlgeom = False
        for skey, step in self.steps.items():
            if step.type in ['STATIC', 'STATIC,RIKS']:
                factor = step.factor
                disp_dic.update(self.scale_displacements(step.displacements, factor))
                loads_dic.update(self.scale_loads(step.loads, factor))
                name += skey + '_'
                if step.nlgeom:
                    nlgeom = True
        self.add_step(GeneralStep(name=name, displacements=disp_dic, loads=loads_dic, type='STATIC', nlgeom=nlgeom))
        return name

# ==============================================================================
# analyse
# ==============================================================================

    def analyse(self, path, name, software, fields, exe=None, cpus=2):
        """ Runs the analysis through the chosen FEA software/library.

        Parameters:
            path (str): Folder to save data.
            name (str): Name of the Structure object and analysis files.
            software (str): Analysis software or library to use, 'abaqus' or 'ansys'.
            fields (str): Data fields to extract e.g 'U,S,SM'.
            exe (str): Full terminal command to bypass subprocess defaults.
            cpus (int): Number of CPU cores to use.

        Returns:
            None
        """
        success = False

        if software == 'abaqus':

            # Create temp folder

            temp = '{0}{1}/'.format(path, name)
            try:
                os.stat(temp)
            except:
                os.mkdir(temp)

            # Save node and elements' nodes data

            nodes = {nkey: self.node_xyz(nkey) for nkey in sorted(self.nodes, key=int)}
            elements = {ekey: self.elements[ekey].nodes for ekey in sorted(self.elements, key=int)}
            with open('{0}{1}-nodes.json'.format(temp, name), 'w') as f:
                json.dump(nodes, f)
            with open('{0}{1}-elements.json'.format(temp, name), 'w') as f:
                json.dump(elements, f)

            # Run sub-process odb.py file

            odb_loc = abaq.__file__.replace('__init__', 'odb')
            subprocess = 'noGUI=' + odb_loc.replace('\\', '/')

            if not exe:
                args = ['abaqus', 'cae', subprocess, '--', fields, str(cpus), temp, path, name]
                p = Popen(args, stdout=PIPE, stderr=PIPE, cwd=temp, shell=True)
                while True:
                    line = p.stdout.readline()
                    if not line:
                        break
                    line = str(line.strip())
                    print(line)
                    if 'COMPLETED' in line:
                        success = True
                stdout, stderr = p.communicate()
                print(stdout)
                print(stderr)

                if not success:
                    try:
                        with open('{0}{1}.msg'.format(temp, name)) as f:
                            lines = f.readlines()
                            for c, line in enumerate(lines):
                                if (' ***ERROR' in line) or (' ***WARNING' in line):
                                    print(lines[c][:-2])
                                    print(lines[c + 1][:-2])
                    except:
                        print('***** Loading .msg log failed *****')

            else:
                args = '{0} -- {1} {2} {3} {4} {5}'.format(subprocess, fields, cpus, temp, path, name)
                os.chdir(temp)
                os.system('{0}{1}'.format(exe, args))

            # Store data

            try:
                with open('{0}{1}-results.json'.format(temp, name), 'r') as f:
                    self.results = json.load(f)
                self.save_to_obj('{0}{1}.obj'.format(path, name))
                print('***** Saving results.json file to structure.results successful *****')
            except:
                print('***** Saving results.json file to structure.results unsuccessful *****')

        elif software == 'ansys':

            ansys.ansys_launch_process(self, path, name)

# ==============================================================================
# summary
# ==============================================================================

    def summary(self):
        """ Prints a summary of the Structure object contents.

        Parameters:
            None

        Returns:
            None
        """
        print(' ')
        print('-' * 50)
        print('Structure summary')
        print('-' * 50)

        print('Nodes: {0}'.format(self.node_count()))
        print('Elements: {0}'.format(self.element_count()))
        print('Sets:')
        for i, set in self.sets.items():
            print('    {0} : {1} {2}(s)'.format(i, len(set['selection']), set['type']))
        print('Materials:')
        for i, material in self.materials.items():
            print('    {0} : {1}'.format(i, material.__name__))
        print('Sections:')
        for i, section in self.sections.items():
            print('    {0} : {1}'.format(i, section.__name__))
        print('Loads:')
        for i, load in self.loads.items():
            print('    {0} : {1}'.format(i, load.__name__))
        print('Displacements:')
        for i, displacement in self.displacements.items():
            print('    {0} : {1}'.format(i, displacement.__name__))
        print('Constraints:')
        for i, constraint in self.constraints.items():
            print('    {0} : {1}'.format(i, constraint.__name__))
        print('Interactions:')
        for i, interaction in self.interactions.items():
            print('    {0} : {1}'.format(i, interaction.__name__))
        print('Misc:')
        for i, misc in self.misc.items():
            print('    {0} : {1}'.format(i, misc.__name__))
        print('Steps:')
        for i, step in self.steps.items():
            if i != 'order':
                print('    {0} : {1}'.format(i, step.__name__))

        print('-' * 50 + '\n')

# ==============================================================================
# app
# ==============================================================================

    def view(self):
        """ Starts the QT app for visualisation.

        Note:
            - In development.

        Parameters:
            None

        Returns:
            None
        """
        try:
            from compas_fea.viewers.app import App
            app = App(self)
            app.start()
        except:
            print('***** Failed to load QT App *****')


# ==============================================================================
# save
# ==============================================================================

    def save_to_obj(self, fnm):
        """ Exports the Structure object to an .obj file through Pickle.

        Parameters:
            fnm (str): Path to save the Structure .obj to.

        Returns:
            None
        """
        with open(fnm, 'wb') as f:
            pickle.dump(self, f)
        print('***** Structure saved as: {0} *****'.format(fnm))


# ==============================================================================
# load
# ==============================================================================

def load_from_obj(fnm):
    """ Imports a Structure object from an .obj file through Pickle.

    Parameters:
        fnm (str): Path to load the Structure .obj from.

    Returns:
        obj: Imported Structure object.
    """
    with open(fnm, 'rb') as f:
        structure = pickle.load(f)
        print('***** Structure loaded from: {0} *****'.format(fnm))
    return structure
