
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.geometry import centroid_points

from compas.utilities import geometric_key

from compas_fea.fea.abaq import abaq
from compas_fea.fea.ansys import ansys
from compas_fea.fea.opensees import opensees
from compas_fea.fea.sofistik import sofistik

from compas_fea.structure import *

from compas_fea.utilities import combine_all_sets
from compas_fea.utilities import group_keys_by_attribute
from compas_fea.utilities import group_keys_by_attributes

import pickle


__author__    = ['Andrew Liew <liew@arch.ethz.ch>', 'Tomas Mendez <mendez@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'Structure',
]


class Structure(object):

    """ Initialises empty Structure object for use in finite element analysis.

    Parameters
    ----------
    name : str
        Name of the structure.
    path : str
        Path to save files.

    Attributes
    ----------
    constraints : dic
        Constraint objects.
    displacements : dic
        Displacement objects.
    elements : dic
        Element objects.
    element_index : dic
        Index of elements (element centroid geometric keys).
    element_properties : dic
        Element properties objects.
    interactions : dic
        Interaction objects.
    loads : dic
        Load objects.
    materials : dic
        Material objects.
    misc : dic
        Misc objects.
    name : str
        Structure name.
    nodes : dic
        Node co-ordinates and local axes.
    node_index : dic
        Index of nodes (node geometric keys).
    path : str
        Path to save files.
    results : dic
        Dictionary containing analysis results.
    sections : dic
        Section objects.
    sets : dic
        Node, element and surface sets.
    steps : dic
        Step objects.
    steps_order : list
        Sorted list of Step object names.
    tol : str
        Geometric key tolerance.

    Returns
    -------
    None

    """

    def __init__(self, name='compas_fea-Structure', path=None):
        self.constraints = {}
        self.displacements = {}
        self.elements = {}
        self.element_index = {}
        self.element_properties = {}
        self.interactions = {}
        self.loads = {}
        self.materials = {}
        self.misc = {}
        self.name = name
        self.nodes = {}
        self.node_index = {}
        self.path = path
        self.results = {}
        self.sections = {}
        self.sets = {}
        self.steps = {}
        self.steps_order = []
        self.tol = '3'
        self.virtual_nodes = {}

    def __str__(self):
        n = self.node_count()
        m = self.element_count()
        data = [
            self.materials,
            self.sections,
            self.loads,
            self.displacements,
            self.constraints,
            self.interactions,
            self.misc,
            self.steps,
        ]

        d = ['\n'.join(['  {0} : {1} {2}(s)'.format(i, len(j['selection']), j['type'])
                        for i, j in self.sets.items() if 'element_' not in i])]
        for entry in data:
            if entry:
                d.append('\n'.join(['  {0} : {1}'.format(i, j.__name__) for i, j in entry.items()]))
            else:
                d.append('  n/a')

        return """

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
compas_fea Structure: {}
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Nodes
-----
{}

Elements
--------
{}

Sets
----
{}

Materials
---------
{}

Sections
--------
{}

Loads
-----
{}

Displacements
-------------
{}

Constraints
-----------
{}

Interactions
------------
{}

Misc
----
{}

Steps
-----
{}

""".format(self.name, n, m, d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7], d[8])


# ==============================================================================
# nodes
# ==============================================================================

    def add_node(self, xyz, ex=[1, 0, 0], ey=[0, 1, 0], ez=[0, 0, 1]):

        """ Adds a node to structure.nodes at co-ordinates xyz with local frame [ex, ey, ez].

        Parameters
        ----------
        xyz : list
            [x, y, z] co-ordinates of the node.
        ex : list
            Node's local x axis.
        ey : list
            Node's local y axis.
        ez : list
            Node's local z axis.

        Returns
        -------
        int
            Key of the added or pre-existing node.

        Notes
        -----
        - Nodes are numbered sequentially starting from 0.

        """

        xyz = [float(i) for i in xyz]
        key = self.check_node_exists(xyz)
        if key is None:
            key = self.node_count()
            self.nodes[key] = {'x': xyz[0], 'y': xyz[1], 'z': xyz[2], 'ex': ex, 'ey': ey, 'ez': ez}
            self.add_node_to_node_index(key=key, xyz=xyz)
        return key

    def add_nodes(self, nodes, ex=[1, 0, 0], ey=[0, 1, 0], ez=[0, 0, 1]):

        """ Adds a list of nodes to structure.nodes at given co-ordinates all with local frame [ex, ey, ez].

        Parameters
        ----------
        nodes : list
            [[x, y, z], ..] co-ordinates for each node.
        ex : list
            Nodes' local x axis.
        ey : list
            Nodes' local y axis.
        ez : list
            Nodes' local z axis.

        Returns
        -------
        list
            Keys of the added or pre-existing nodes.

        Notes
        -----
        - Nodes are numbered sequentially starting from 0.

        """

        return [self.add_node(xyz=node, ex=ex, ey=ey, ez=ez) for node in nodes]

    def add_node_to_node_index(self, key, xyz):

        """ Adds the node to the node_index dictionary.

        Parameters
        ----------
        key : int
            Prescribed node key.
        xyz : list
            [x, y, z] co-ordinates of the node.

        Returns
        -------
        None

        """

        gkey = geometric_key(xyz, '{0}f'.format(self.tol))
        self.node_index[gkey] = key

    def check_node_exists(self, xyz):

        """ Check if a node already exists at given x, y, z co-ordinates.

        Parameters
        ----------
        xyz : list
            [x, y, z] co-ordinates of node to check.

        Returns
        -------
        int
            The node index if the node already exists, None if not.

        Notes
        -----
        - Geometric key check is made according to self.tol [m] tolerance.

        """

        gkey = geometric_key(xyz, '{0}f'.format(self.tol))
        return self.node_index.get(gkey, None)

    def edit_node(self, key, attr_dic):

        """ Edit a node's data.

        Parameters
        ----------
        key : int
            Key of the node to edit.
        attr_dic : dic
            Atribute dictionary of data to edit.

        Returns
        -------
        None

        """

        gkey = geometric_key(self.node_xyz(key), '{0}f'.format(self.tol))
        del self.node_index[gkey]
        for attr, item in attr_dic.items():
            self.nodes[key][attr] = item
        self.add_node_to_node_index(key, self.node_xyz(key))

    def make_node_index_dic(self):

        """ Makes a node_index dictionary from existing structure.nodes.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        for key in self.nodes:
            gkey = geometric_key(self.node_xyz(key), '{0}f'.format(self.tol))
            self.node_index[gkey] = key

    def node_bounds(self):

        """ Return the bounds formed by the Structure's nodal co-ordinates.

        Parameters
        ----------
        None

        Returns
        -------
        list
            [xmin, xmax].
        list
            [ymin, ymax].
        list
            [zmin, zmax].

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

        Parameters
        ----------
        None

        Returns
        -------
        int
            Number of nodes stored in the Structure object.

        """

        return len(self.nodes)

    def node_xyz(self, node):

        """ Return the xyz co-ordinates of a node.

        Parameters
        ----------
        node : int
            Node number.

        Returns
        -------
        list
            [x, y, z] co-ordinates.

        """

        return [self.nodes[node][i] for i in 'xyz']

    def nodes_xyz(self, nodes=[]):

        """ Return the xyz co-ordinates of given or all nodes.

        Parameters
        ----------
        nodes : list
            Node numbers, else all will be given.

        Returns
        -------
        list
            [[x, y, z] ...] co-ordinates.

        """

        if not nodes:
            nodes = sorted(self.nodes, key=int)
        return [self.node_xyz(node=node) for node in nodes]


# ==============================================================================
# elements
# ==============================================================================

    def add_element(self, nodes, type, acoustic=False, thermal=False, axes={}):

        """ Adds an element to structure.elements with centroid geometric key.

        Parameters
        ----------
        nodes : list
            Nodes the element is connected to.
        type : str
            Element type: 'HexahedronElement', 'BeamElement, 'TrussElement' etc.
        acoustic : bool
            Acoustic properties on or off.
        thermal : bool
            Thermal properties on or off.
        axes : dic
            The local element axes 'ex', 'ey' and 'ez'.

        Returns
        -------
        int
            Key of the added or existing element.

        Notes
        -----
        - Elements are numbered sequentially starting from 0.

        """

        func_dic = {
            'BeamElement':        BeamElement,
            'SpringElement':      SpringElement,
            'TrussElement':       TrussElement,
            'StrutElement':       StrutElement,
            'TieElement':         TieElement,
            'ShellElement':       ShellElement,
            'MembraneElement':    MembraneElement,
            'SolidElement':       SolidElement,
            'TetrahedronElement': TetrahedronElement,
            'PentahedronElement': PentahedronElement,
            'HexahedronElement':  HexahedronElement,
        }

        ekey = self.check_element_exists(nodes)
        if ekey is None:
            ekey = self.element_count()
            element = func_dic[type]()
            element.axes = axes
            element.nodes = nodes
            element.number = ekey
            element.acoustic = acoustic
            element.thermal = thermal
            self.elements[ekey] = element
            self.add_element_to_element_index(ekey, nodes)
        return ekey

    def add_elements(self, elements, type, acoustic=False, thermal=False, axes={}):

        """ Adds multiple elements of the same type to structure.elements.

        Parameters
        ----------
        elements : list
            List of lists of the nodes the elements are connected to.
        type : str
            Element type: 'HexahedronElement', 'BeamElement, 'TrussElement' etc.
        acoustic : bool
            Acoustic properties on or off.
        thermal : bool
            Thermal properties on or off.
        axes : dic
            The local element axes 'ex', 'ey' and 'ez' for all elements.

        Returns
        -------
        list
            Keys of the added or existing elements.

        Notes
        -----
        - Elements are numbered sequentially starting from 0.

        """

        return [self.add_element(nodes=nodes, type=type, acoustic=acoustic, thermal=thermal, axes=axes)
                for nodes in elements]

    def add_element_to_element_index(self, key, nodes):

        """ Adds the element to the element_index dictionary.

        Parameters
        ----------
        key : int
            Prescribed element key.
        nodes : list
            Node numbers the element is connected to.

        Returns
        -------
        None

        """

        centroid = centroid_points([self.node_xyz(node) for node in nodes])
        gkey = geometric_key(centroid, '{0}f'.format(self.tol))
        self.element_index[gkey] = key

    def check_element_exists(self, nodes, xyz=None):

        """ Check if an element already exists based on the nodes it connects to or its centroid.

        Parameters
        ----------
        nodes : list
            Node numbers the element is connected to.
        xyz : list
            Direct co-ordinates of the element centroid to check.

        Returns
        -------
        int
            The element index if the element already exists, None if not.

        Notes
        -----
        - Geometric key check is made according to self.tol [m] tolerance.

        """

        if not xyz:
            xyz = centroid_points([self.node_xyz(node) for node in nodes])
        gkey = geometric_key(xyz, '{0}f'.format(self.tol))
        return self.element_index.get(gkey, None)

    def edit_element(self):
        raise NotImplementedError

    def element_count(self):

        """ Return the number of elements in structure.elements.

        Parameters
        ----------
        None

        Returns
        -------
        int
            Number of elements stored in the Structure object.

        """

        return len(self.elements)

    def make_element_index_dic(self):

        """ Makes an element_index dictionary from existing structure.elements.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        for key, element in self.elements.items():
            self.add_element_to_element_index(key=key, nodes=element.nodes)

    def element_centroid(self, element):

        """ Return the centroid of an element.

        Parameters
        ----------
        element : int
            Number of the element.

        Returns
        -------
        list
            Co-ordinates of the element centroid.

        """

        nodes = self.elements[element].nodes
        return centroid_points([self.node_xyz(node) for node in nodes])

    def add_nodal_element(self, node, type, virtual_node=False):

        """ Adds a nodal element to structure.elements with the possibility of
        adding a coincident virtual node. Virtual nodes are added to a node
        set called 'virtual_nodes'.

        Parameters
        ----------
        node : int
            Node number the element is connected to.
        type : str
            Element type: 'SpringElement'.
        virtual_node : bool
            Create a virtual node or not.

        Returns
        -------
        int
            Key of the added element.

        Notes
        -----
        - Elements are numbered sequentially starting from 0.

        """

        if virtual_node:
            xyz = self.node_xyz(node)
            key = self.virtual_nodes.setdefault(node, self.node_count())
            self.nodes[key] = {'x': xyz[0], 'y': xyz[1], 'z': xyz[2],
                               'ex': [1, 0, 0], 'ey': [0, 1, 0], 'ez': [0, 0, 1], 'virtual': True}
            if 'virtual_nodes' in self.sets:
                self.sets['virtual_nodes']['selection'].append(key)
            else:
                self.sets['virtual_nodes'] = {'type': 'node', 'selection': [key], 'explode': False}
            nodes = [node, key]
        else:
            nodes = [node]

        func_dic = {
            'SpringElement': SpringElement,
        }

        ekey = self.element_count()
        element = func_dic[type]()
        element.nodes = nodes
        element.number = ekey
        self.elements[ekey] = element
        return ekey


# ==============================================================================
# sets
# ==============================================================================

    def add_set(self, name, type, selection):

        """ Adds a node, element or surface set to structure.sets.

        Parameters
        ----------
        name : str
            Name of the set.
        type : str
            'node', 'element', 'surface_node', surface_element'.
        selection : list, dic
            The integer keys of the nodes, elements or the element numbers and sides.

        Returns
        -------
        None

        """

        if isinstance(selection, int):
            selection = [selection]
        self.sets[name] = {'type': type, 'selection': selection, 'index': len(self.sets)}


# ==============================================================================
# constructors
# ==============================================================================

    @classmethod
    def from_mesh(cls, mesh):

        """ Creates a Structure object based on data contained in a compas Mesh
        datastructure. The Mesh object must contain displacements, materials, sections
        and loads.

        Parameters
        ----------
        mesh : obj
            Mesh datastructure object.

        Returns
        -------
        obj
            The resulting Structure object.

        """

        structure = cls()

        # Add nodes and elements from Mesh

        structure.add_nodes_elements_from_mesh(mesh=mesh, type='ShellElement')

        # Add displacements

        disp_groups = group_keys_by_attributes(mesh.vertex, ['ux', 'uy', 'uz', 'urx', 'ury', 'urz'])
        disp_names = []
        for dk in disp_groups:
            if dk != '-_-_-_-_-_-':
                disp_names.append(dk + '_nodes')
                structure.add_set(name=dk, type='node', selection=disp_groups[dk])
                d = [float(x) if x != '-' else None for x in dk.split('_')]
                supports = GeneralDisplacement(name=dk + '_nodes', nodes=dk, x=d[0], y=d[1], z=d[2],
                                               xx=d[3], yy=d[4], zz=d[5])
                structure.add_displacement(supports)

        # Add materials and sections

        mat_groups = group_keys_by_attributes(mesh.facedata, ['E', 'v', 'p'])
        for mk in mat_groups:
            m = [float(x) if x != '-' else None for x in mk.split('_')]
            material = ElasticIsotropic(name=mk + '_material', E=m[0], v=m[1], p=m[2])
            structure.add_material(material)

        thick_groups = group_keys_by_attribute(mesh.facedata, 'thick')
        for tk in thick_groups:
            t = float(tk)
            section = ShellSection(name=tk + '_section', t=t)
            structure.add_section(section)

        prop_comb = combine_all_sets(mat_groups, thick_groups)
        for pk in prop_comb:
            mat, sec = pk.split(',')
            prop = ElementProperties(material=mat + '_material', section=sec + '_section', elements=prop_comb[pk])
            structure.add_element_properties(prop)

        # Add loads

        load_groups = group_keys_by_attribute(mesh.vertex, 'l')
        load_names = []
        for lk in load_groups:
            if lk != '-':
                load_names.append(str(lk) + '_load')
                nkeys = load_groups[lk]
                load = PointLoad(name=str(lk) + '_load', nodes=nkeys, x=lk[0], y=lk[1], z=lk[2])
                structure.add_load(load)

        gstep = GeneralStep(name='Structure from Mesh', displacements=disp_names, loads=load_names)
        structure.add_step(gstep)

        return structure

    @classmethod
    def from_network(self, network):
        pass

    def add_nodes_elements_from_mesh(self, mesh, element_type, acoustic=False, thermal=False, elset=None):

        """ Adds the nodes and faces of a Mesh to the Structure object.

        Parameters
        ----------
        mesh : obj
            Mesh datastructure object.
        element_type : str
            Element type: 'ShellElement', 'MembraneElement' etc.
        acoustic : bool
            Acoustic properties on or off.
        thermal : bool
            Thermal properties on or off.
        elset : str
            Name of element set to create.

        Returns
        -------
        list
            Keys of the created elements.

        """

        for key in sorted(list(mesh.vertices()), key=int):
            self.add_node(mesh.vertex_coordinates(key))
        ekeys = []
        for fkey in list(mesh.faces()):
            face = [self.check_node_exists(mesh.vertex_coordinates(i)) for i in mesh.face[fkey]]
            ekeys.append(self.add_element(nodes=face, type=element_type, acoustic=acoustic, thermal=thermal))
        if elset:
            self.add_set(name=elset, type='element', selection=ekeys)
        return ekeys

    def add_nodes_elements_from_network(self, network, element_type, acoustic=False, thermal=False, elset=None, axes={}):

        """ Adds the nodes and edges of a Network to the Structure object.

        Parameters
        ----------
        network : obj
            Network datastructure object.
        element_type : str
            Element type: 'BeamElement', 'TrussElement' etc.
        acoustic : bool
            Acoustic properties on or off.
        thermal : bool
            Thermal properties on or off.
        elset : str
            Name of element set to create.
        axes : dic
            The local element axes 'ex', 'ey' and 'ez' for all elements.

        Returns
        -------
        list
            Keys of the created elements.

        """

        for key in sorted(list(network.vertices()), key=int):
            self.add_node(network.vertex_coordinates(key))
        ekeys = []
        for u, v in list(network.edges()):
            sp = self.check_node_exists(network.vertex_coordinates(u))
            ep = self.check_node_exists(network.vertex_coordinates(v))
            ekeys.append(self.add_element(nodes=[sp, ep], type=element_type, acoustic=acoustic, thermal=thermal,
                                          axes=axes))
        if elset:
            self.add_set(name=elset, type='element', selection=ekeys)
        return ekeys


# ==============================================================================
# modifiers
# ==============================================================================

    def scale_displacements(self, displacements, factor):

        """ Scales displacements by a given factor.

        Parameters
        ----------
        displacements : dic
            Dictionary containing the displacements to scale.
        factor : float
            Factor to scale the displacements by.

        Returns
        -------
        dic
            The scaled displacements dictionary.

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

        Parameters
        ----------
        loads : dic
            Dictionary containing the loads to scale.
        factor : float
            Factor to scale the loads by.

        Returns
        -------
        dic
            The scaled loads dictionary.

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

        Parameters
        ----------
        constraint : obj
            The Constraint object.

        Returns
        -------
        None

        """

        constraint.index = len(self.constraints)
        self.constraints[constraint.name] = constraint

    def add_displacement(self, displacement):

        """ Adds a Displacement object to structure.displacements.

        Parameters
        ----------
        displacement : obj
            The Displacement object.

        Returns
        -------
        None

        """

        displacement.index = len(self.displacements)
        self.displacements[displacement.name] = displacement

    def add_displacements(self, displacements):

        """ Adds Displacement objects to structure.displacements.

        Parameters
        ----------
        displacements : list
            The Displacement objects.

        Returns
        -------
        None

        """

        for displacement in displacements:
            self.add_displacement(displacement)

    def add_element_properties(self, element_properties):

        """ Adds ElementProperties object(s) to structure.element_properties.

        Parameters
        ----------
        element_properties : obj, list
            The ElementProperties object(s).

        Returns
        -------
        None

        """

        if isinstance(element_properties, list):
            for element_property in element_properties:
                element_property.index = len(self.element_properties)
                self.element_properties[element_property.name] = element_property
        else:
            element_properties.index = len(self.element_properties)
            self.element_properties[element_properties.name] = element_properties

    def add_interaction(self, interaction):

        """ Adds an Interaction object to structure.interactions.

        Parameters
        ----------
        interaction : obj
            The Interaction object.

        Returns
        -------
        None

        """

        interaction.index = len(self.interactions)
        self.interactions[interaction.name] = interaction

    def add_load(self, load):

        """ Adds a Load object to structure.loads.

        Parameters
        ----------
        load : obj
            The Load object.

        Returns
        -------
        None

        """

        load.index = len(self.loads)
        self.loads[load.name] = load

    def add_loads(self, loads):

        """ Adds Load objects to structure.loads.

        Parameters
        ----------
        loads : list
            The Load objects.

        Returns
        -------
        None

        """

        for load in loads:
            self.add_load(load)

    def add_material(self, material):

        """ Adds a Material object to structure.materials.

        Parameters
        ----------
        material : obj
            The Material object.

        Returns
        -------
        None

        """

        material.index = len(self.materials)
        self.materials[material.name] = material

    def add_materials(self, materials):

        """ Adds Material objects to structure.materials.

        Parameters
        ----------
        materials : list
            The Material objects.

        Returns
        -------
        None

        """

        for material in materials:
            self.add_material(material)

    def add_misc(self, misc):

        """ Adds a Misc object to structure.misc.

        Parameters
        ----------
        misc : obj
            The Misc object.

        Returns
        -------
        None

        """

        misc.index = len(self.misc)
        self.misc[misc.name] = misc

    def add_section(self, section):

        """ Adds a Section object to structure.sections.

        Parameters
        ----------
        section : obj
            The Section object.

        Returns
        -------
        None

        """

        section.index = len(self.sections)
        self.sections[section.name] = section

    def add_sections(self, sections):

        """ Adds Section objects to structure.sections.

        Parameters
        ----------
        sections : list
            The Section objects.

        Returns
        -------
        None

        """

        for section in sections:
            self.add_section(section)

    def add_step(self, step):

        """ Adds a Step object to structure.steps.

        Parameters
        ----------
        step : obj
            The Step object.

        Returns
        -------
        None

        """

        step.index = len(self.steps)
        self.steps[step.name] = step

    def add_steps(self, steps):

        """ Adds Step objects to structure.steps.

        Parameters
        ----------
        steps : list
            The Step objects.

        Returns
        -------
        None

        """

        for step in steps:
            self.add_step(step)


# ==============================================================================
# steps
# ==============================================================================

    def set_steps_order(self, order):

        """ Sets the order the Steps will be analysed.

        Parameters
        ----------
        order : list
            An ordered list of the Step names.

        Returns
        -------
        None

        """

        self.steps_order = order


# ==============================================================================
# analysis
# ==============================================================================

    def fields_dic_from_list(self, fields_list):

        """ Creates a fields dictionary from a fields list.

        Parameters
        ----------
        fields_list : list
            List of fields and/or components.

        Returns
        -------
        dic
            Conversion to a fields dictionary.

        """

        node_fields = ['rf', 'rm', 'u', 'ur', 'cf', 'cm']
        element_fields = ['sf', 'sm', 'sk', 'se', 's', 'e', 'pe', 'rbfor', 'spf']

        fields_dic = {}

        for field in node_fields + element_fields:
            if field in fields_list:
                fields_dic[field] = 'all'

        return fields_dic

    def write_input_file(self, software, fields='u'):

        """ Writes the FE software's input file.

        Parameters
        ----------
        software : str
            Analysis software or library to use, 'abaqus', 'opensees' or 'ansys'.
        fields : list, str
            Data field requests.

        Returns
        -------
        None

        """

        self.save_to_obj()

        if software == 'abaqus':
            abaq.input_generate(self, fields=fields)

        elif software == 'ansys':
            ansys.input_generate(self)

        elif software == 'opensees':
            opensees.input_generate(self, fields=fields)

        elif software == 'sofistik':
            sofistik.input_generate(self, fields=fields)

    def analyse(self, software, exe=None, cpus=1, license='research', delete=True):

        """ Runs the analysis through the chosen FEA software/library.

        Parameters
        ----------
        software : str
            Analysis software or library to use, 'abaqus', 'opensees' or 'ansys'.
        exe : str
            Full terminal command to bypass subprocess defaults.
        cpus : int
            Number of CPU cores to use.
        license : str
            FE software license type (if required): 'research', 'student'.

        Returns
        -------
        None

        """

        if software == 'abaqus':
            abaq.abaqus_launch_process(self, exe, cpus)

        elif software == 'ansys':
            ansys.ansys_launch_process(self.path, self.name, cpus, license, delete=delete)

        elif software == 'opensees':
            opensees.opensees_launch_process(self, exe)

    def extract_data(self, software, fields='u', steps='last', exe=None):

        """ Extracts data from the FE software's output.

        Parameters
        ----------
        software : str
            Analysis software or library used, 'abaqus', 'opensees' or 'ansys'.
        fields : list, str
            Data field requests.
        steps : list
            Loads steps to extract from.
        exe : str
            Full terminal command to bypass subprocess defaults.

        Returns
        -------
        None

        """

        if software == 'abaqus':
            abaq.extract_odb_data(self, fields=fields, exe=exe)

        elif software == 'ansys':
            ansys.extract_rst_data(self, fields=fields, steps=steps)

        elif software == 'opensees':
            opensees.extract_out_data(self, fields=fields)

    def analyse_and_extract(self, software, fields='u', exe=None, cpus=1, license='research'):

        """ Runs the analysis through the chosen FEA software/library and extracts data.

        Parameters
        ----------
        software : str
            Analysis software or library to use, 'abaqus', 'opensees' or 'ansys'.
        fields : list, str
            Data field requests.
        exe : str
            Full terminal command to bypass subprocess defaults.
        cpus : int
            Number of CPU cores to use.
        license : str
            FE software license type (if required): 'research', 'student'.

        Returns
        -------
        None

        """

        self.write_input_file(software=software, fields=fields)
        self.analyse(software=software, exe=exe, cpus=cpus, license=license)
        self.extract_data(software=software, fields=fields, exe=exe)


# ==============================================================================
# results
# ==============================================================================

    def get_nodal_results(self, step, field, nodes='all'):

        """ Extract nodal results from self.results.

        Parameters
        ----------
        step : str
            Step to extract from.
        field : str
            Data field request.
        nodes : str, list
            Extract 'all' or a node set/list.

        Returns
        -------
        dic
            The nodal results for the requested field.

        """

        data = {}
        rdict = self.results[step]['nodal']

        if nodes == 'all':
            keys = list(self.nodes.keys())
        elif isinstance(nodes, str):
            keys = self.sets[nodes]['selection']
        else:
            keys = nodes

        for key in keys:
            data[key] = rdict[field][key]
        return data

    def get_element_results(self, step, field, elements='all'):

        """ Extract element results from self.results.

        Parameters
        ----------
        step : str
            Step to extract from.
        field : str
            Data field request.
        elements : str, list
            Extract 'all' or an element set/list.

        Returns
        -------
        dic
            The element results for the requested field.

        """

        data = {}
        rdict = self.results[step]['element']

        if elements == 'all':
            keys = list(self.elements.keys())
        elif isinstance(elements, str):
            keys = self.sets[elements]['selection']
        else:
            keys = elements

        for key in keys:
            data[key] = rdict[field][key]
        return data


# ==============================================================================
# summary
# ==============================================================================

    def summary(self):

        """ Prints a summary of the Structure object contents.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        print(self)


# ==============================================================================
# app
# ==============================================================================

    def view(self):

        """ Starts the Pyside app for visualisation.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        - In development.

        """

        try:
            print('***** Launching App *****')

            xb, yb, zb = self.node_bounds()
            xm = 0.5 * (xb[0] + xb[1])
            ym = 0.5 * (yb[0] + yb[1])
            zm = 0.5 * (zb[0] + zb[1])

            from compas_fea.app.app import App

            app = App(structure=self)
            app.settings['draw_axes'] = False
            app.settings['vertex_size'] = 0.01
            app.settings['camera_focus'] = [xm, ym, zm]
            app.start()

        except:
            print('***** Launching App failed *****')


# ==============================================================================
# save
# ==============================================================================

    def save_to_obj(self):

        """ Exports the Structure object to an .obj file through Pickle.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        filename = '{0}{1}.obj'.format(self.path, self.name)
        with open(filename, 'wb') as f:
            pickle.dump(self, f)
        print('***** Structure saved to: {0} *****\n'.format(filename))


# ==============================================================================
# load
# ==============================================================================

    @staticmethod
    def load_from_obj(filename):

        """ Imports a Structure object from an .obj file through Pickle.

        Parameters
        ----------
        filename : str
            Path to load the Structure .obj from.

        Returns
        -------
        obj
            Imported Structure object.

        """

        with open(filename, 'rb') as f:
            structure = pickle.load(f)
            print('***** Structure loaded from: {0} *****'.format(filename))
        return structure
