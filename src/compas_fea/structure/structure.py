from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas_fea.fea.abaq import abaq
from compas_fea.fea.ansys import ansys
from compas_fea.fea.opensees import opensees

# from compas_fea.utilities import combine_all_sets
# from compas_fea.utilities import group_keys_by_attribute
# from compas_fea.utilities import group_keys_by_attributes

from compas_fea.structure.mixins.nodemixins import NodeMixins
from compas_fea.structure.mixins.elementmixins import ElementMixins
from compas_fea.structure.mixins.objectmixins import ObjectMixins
# from compas_fea.structure.displacement import *
from compas_fea.structure.set import Set

import pickle
import os


# Author(s): Andrew Liew (github.com/andrewliew), Tomas Mendez Echenagucia (github.com/tmsmendez)


__all__ = [
    'Structure',
]


class Structure(ObjectMixins, ElementMixins, NodeMixins):
    """Initialises Structure object for use in finite element analysis.

    Parameters
    ----------
    path : str
        Path to save all compas_fea associated files.
    name : str
        Name of the structure.

    Attributes
    ----------
    constraints : dict
        Constraint objects.
    displacements : dict
        Displacement objects.
    elements : dict
        Element objects.
    element_index : dict
        Index of elements (element centroid geometric keys).
    element_properties : dict
        ElementProperties objects.
    interactions : dict
        Interaction objects.
    loads : dict
        Load objects.
    materials : dict
        Material objects.
    misc : dict
        Misc objects.
    name : str
        Structure name.
    nodes : dict
        Node objects.
    node_index : dict
        Index of nodes (node geometric keys).
    path : str
        Path to save files.
    results : dict
        Dictionary containing analysis results.
    sections : dict
        Section objects.
    sets : dict
        Set objects.
    steps : dict
        Step objects.
    steps_order : list
        Sorted list of Step object names.
    tol : str
        Geometric key tolerance.
    virtual_nodes : dict
        Node objects for virtual nodes.
    virtual_elements : dict
        Element objects for virtual elements.
    virtual_element_index : dict
        Index of virtual elements (element centroid geometric keys).

    """

    def __init__(self, path, name='compas_fea-Structure'):
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
        self.virtual_node_index = {}
        self.virtual_elements = {}
        self.virtual_element_index = {}

    def __str__(self):
        n = self.node_count()
        m = self.element_count()
        data = [
            self.sets,
            self.materials,
            self.sections,
            self.loads,
            self.displacements,
            self.constraints,
            self.interactions,
            self.misc,
            self.steps,
        ]

        d = []

        for entry in data:

            if entry:
                d.append('\n'.join(['  {0} : {1}'.format(i, j.__name__) for i, j in entry.items()]))
            else:
                d.append('n/a')

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
    # Sets
    # ==============================================================================

    def add_set(self, name, type, selection):
        """Adds a node, element or surface set to structure.sets.

        Parameters
        ----------
        name : str
            Name of the Set.
        type : str
            'node', 'element', 'surface_node', surface_element'.
        selection : list, dict
            The integer keys of the nodes, elements or the element numbers and sides.

        Returns
        -------
        None

        """

        if isinstance(selection, int):
            selection = [selection]

        self.sets[name] = Set(name=name, type=type, selection=selection, index=len(self.sets))

    # ==============================================================================
    # Constructors    EXPERIMENTAL
    # ==============================================================================

    # @classmethod
    # def from_mesh(cls, mesh, path):

    #     """Creates a Structure object based on data contained in a compas Mesh datastructure.

    #     Parameters
    #     ----------
    #     mesh : obj
    #         Mesh datastructure object.

    #     Returns
    #     -------
    #     obj
    #         The resulting Structure object.

    #     Notes
    #     -----
    #     - The Mesh object must contain displacements, materials, sections and loads.

    #     """

    #     structure = cls(path=path)

    #     # Add nodes and elements from Mesh

    #     structure.add_nodes_elements_from_mesh(mesh=mesh, element_type='ShellElement')

    #     # Add displacements

    #     disp_groups = group_keys_by_attributes(mesh.vertex, ['ux', 'uy', 'uz', 'urx', 'ury', 'urz'])
    #     disp_names  = []

    #     for dk in disp_groups:
    #         if dk != '-_-_-_-_-_-':
    #             disp_names.append(dk + '_nodes')
    #             structure.add_set(name=dk, type='node', selection=disp_groups[dk])
    #             d = [float(x) if x != '-' else None for x in dk.split('_')]
    #             supports = GeneralDisplacement(name=dk + '_nodes', nodes=dk, x=d[0], y=d[1], z=d[2],
    #                                            xx=d[3], yy=d[4], zz=d[5])
    #             structure.add_displacement(supports)

    #     # Add materials and sections

    #     mat_groups = group_keys_by_attributes(mesh.facedata, ['E', 'v', 'p'])

    #     for mk in mat_groups:
    #         m = [float(x) if x != '-' else None for x in mk.split('_')]
    #         material = ElasticIsotropic(name=mk + '_material', E=m[0], v=m[1], p=m[2])
    #         structure.add_material(material)

    #     thick_groups = group_keys_by_attribute(mesh.facedata, 'thick')

    #     for tk in thick_groups:
    #         t = float(tk)
    #         section = ShellSection(name=tk + '_section', t=t)
    #         structure.add_section(section)

    #     prop_comb = combine_all_sets(mat_groups, thick_groups)

    #     for pk in prop_comb:
    #         mat, sec = pk.split(',')
    #         prop = ElementProperties(material=mat + '_material', section=sec + '_section', elements=prop_comb[pk])
    #         structure.add_element_properties(prop)

    #     # Add loads

    #     load_groups = group_keys_by_attribute(mesh.vertex, 'l')
    #     load_names  = []

    #     for lk in load_groups:
    #         if lk != '-':
    #             load_names.append(str(lk) + '_load')
    #             nkeys = load_groups[lk]
    #             load = PointLoad(name=str(lk) + '_load', nodes=nkeys, x=lk[0], y=lk[1], z=lk[2])
    #             structure.add_load(load)

    #     gstep = GeneralStep(name='Structure from Mesh', displacements=disp_names, loads=load_names)
    #     structure.add_step(gstep)

    #     return structure

    # @classmethod
    # def from_network(cls, network):

    #     pass

    # @classmethod
    # def from_volmesh(cls, network):

    #     pass

    def add_nodes_elements_from_mesh(self, mesh, element_type, thermal=False, elset=None):
        """Adds the nodes and faces of a Mesh to the Structure object.

        Parameters
        ----------
        mesh : obj
            Mesh datastructure object.
        element_type : str
            Element type: 'ShellElement', 'MembraneElement' etc.
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
            ekeys.append(self.add_element(nodes=face, type=element_type, thermal=thermal))

        if elset:
            self.add_set(name=elset, type='element', selection=ekeys)

        return ekeys

    def add_nodes_elements_from_network(self, network, element_type, thermal=False, elset=None, axes={}):
        """Adds the nodes and edges of a Network to the Structure object.

        Parameters
        ----------
        network : obj
            Network datastructure object.
        element_type : str
            Element type: 'BeamElement', 'TrussElement' etc.
        thermal : bool
            Thermal properties on or off.
        elset : str
            Name of element set to create.
        axes : dict
            The local element axes 'ex', 'ey' and 'ez' for all elements.

        Returns
        -------
        list
            Keys of the created elements.

        """

        for key in sorted(list(network.nodes()), key=int):
            self.add_node(network.node_coordinates(key))

        ekeys = []

        for u, v in list(network.edges()):
            sp = self.check_node_exists(network.node_coordinates(u))
            ep = self.check_node_exists(network.node_coordinates(v))
            ekeys.append(self.add_element(nodes=[sp, ep], type=element_type, thermal=thermal, axes=axes))

        if elset:
            self.add_set(name=elset, type='element', selection=ekeys)

        return ekeys

    def add_nodes_elements_from_volmesh(self, volmesh, element_type='SolidElement', acoustic=False, thermal=False, elset=None, axes={}):
        """Adds the nodes and cells of a VolMesh to the Structure object.

        Parameters
        ----------
        volmesh : obj
            VolMesh datastructure object.
        element_type : str
            Element type: 'SolidElement' or ....
        acoustic : bool
            Acoustic properties on or off.
        thermal : bool
            Thermal properties on or off.
        elset : str
            Name of element set to create.
        axes : dict
            The local element axes 'ex', 'ey' and 'ez' for all elements.

        Returns
        -------
        list
            Keys of the created elements.

        """

        for key in sorted(list(volmesh.vertices()), key=int):
            self.add_node(volmesh.vertex_coordinates(key))

        ekeys = []

        for ckey in volmesh.cell:
            cell_vertices = volmesh.cell_vertices(ckey)
            nkeys = [self.check_node_exists(volmesh.vertex_coordinates(nk)) for nk in cell_vertices]
            ekeys.append(self.add_element(nodes=nkeys, type=element_type, acoustic=acoustic, thermal=thermal,
                                          axes=axes))
        if elset:
            self.add_set(name=elset, type='element', selection=ekeys)

        return ekeys

    # ==============================================================================
    # Modifiers
    # ==============================================================================

    def scale_displacements(self, displacements, factor):
        """Scales displacements by a given factor.

        Parameters
        ----------
        displacements : dict
            Dictionary containing the displacements to scale.
        factor : float
            Factor to scale the displacements by.

        Returns
        -------
        dict
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
        """Scales loads by a given factor.

        Parameters
        ----------
        loads : dict
            Dictionary containing the loads to scale.
        factor : float
            Factor to scale the loads by.

        Returns
        -------
        dict
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
    # Steps
    # ==============================================================================

    def set_steps_order(self, order):
        """Sets the order that the Steps will be analysed.

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
    # Analysis
    # ==============================================================================

    def write_input_file(self, software, fields='u', output=True, save=False, ndof=6):
        """Writes the FE software's input file.

        Parameters
        ----------
        software : str
            Analysis software / library to use, 'abaqus', 'opensees', or 'ansys'.
        fields : list, str
            Data field requests.
        output : bool
            Print terminal output.
        save : bool
            Save structure to .obj before file writing.

        Returns
        -------
        None

        """

        if save:
            self.save_to_obj()

        if software == 'abaqus':
            abaq.input_generate(self, fields=fields, output=output)

        elif software == 'ansys':
            ansys.input_generate(self)

        elif software == 'opensees':
            opensees.input_generate(self, fields=fields, output=output, ndof=ndof)

    def analyse(self, software, exe=None, cpus=4, license='research', delete=True, output=True):
        """Runs the analysis through the chosen FEA software / library.

        Parameters
        ----------
        software : str
            Analysis software / library to use, 'abaqus', 'opensees' or 'ansys'.
        exe : str
            Full terminal command to bypass subprocess defaults.
        cpus : int
            Number of CPU cores to use.
        license : str
            Software license type: 'research', 'student'.
        delete : bool
            -
        output : bool
            Print terminal output.

        Returns
        -------
        None

        """

        if software == 'abaqus':
            cpus = 1 if license == 'student' else cpus
            abaq.launch_process(self, exe=exe, cpus=cpus, output=output)

        elif software == 'ansys':
            ansys.ansys_launch_process(self.path, self.name, cpus, license, delete=delete)

        elif software == 'opensees':
            opensees.launch_process(self, exe=exe, output=output)

    def extract_data(self, software, fields='u', steps='all', exe=None, sets=None, license='research', output=True,
                     return_data=True, components=None):
        """Extracts data from the analysis output files.

        Parameters
        ----------
        software : str
            Analysis software / library to use, 'abaqus', 'opensees' or 'ansys'.
        fields : list, str
            Data field requests.
        steps : list
            Loads steps to extract from.
        exe : str
            Full terminal command to bypass subprocess defaults.
        sets : list
            -
        license : str
            Software license type: 'research', 'student'.
        output : bool
            Print terminal output.
        return_data : bool
            Return data back into structure.results.
        components : list
            Specific components to extract from the fields data.

        Returns
        -------
        None

        """

        if software == 'abaqus':
            abaq.extract_data(self, fields=fields, exe=exe, output=output, return_data=return_data,
                              components=components)

        elif software == 'ansys':
            ansys.extract_rst_data(self, fields=fields, steps=steps, sets=sets, license=license)

        elif software == 'opensees':
            opensees.extract_data(self, fields=fields)

    def analyse_and_extract(self, software, fields='u', exe=None, cpus=4, license='research', output=True, save=False,
                            return_data=True, components=None, ndof=6):
        """Runs the analysis through the chosen FEA software / library and extracts data.

        Parameters
        ----------
        software : str
            Analysis software / library to use, 'abaqus', 'opensees' or 'ansys'.
        fields : list, str
            Data field requests.
        exe : str
            Full terminal command to bypass subprocess defaults.
        cpus : int
            Number of CPU cores to use.
        license : str
            Software license type: 'research', 'student'.
        output : bool
            Print terminal output.
        save : bool
            Save the structure to .obj before writing.
        return_data : bool
            Return data back into structure.results.
        components : list
            Specific components to extract from the fields data.

        Returns
        -------
        None

        """

        self.write_input_file(software=software, fields=fields, output=output, save=save, ndof=ndof)

        self.analyse(software=software, exe=exe, cpus=cpus, license=license, output=output)

        self.extract_data(software=software, fields=fields, exe=exe, license=license, output=output,
                          return_data=return_data, components=components)

    # ==============================================================================
    # Results
    # ==============================================================================

    def get_nodal_results(self, step, field, nodes='all'):
        """Extract nodal results from self.results.

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
        dict
            The nodal results for the requested field.

        """

        data = {}
        rdict = self.results[step]['nodal']

        if nodes == 'all':
            keys = list(self.nodes.keys())

        elif isinstance(nodes, str):
            keys = self.sets[nodes].selection

        else:
            keys = nodes

        for key in keys:
            data[key] = rdict[field][key]

        return data

    def get_element_results(self, step, field, elements='all'):
        """Extract element results from self.results.

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
        dict
            The element results for the requested field.

        """

        data = {}
        rdict = self.results[step]['element']

        if elements == 'all':
            keys = list(self.elements.keys())

        elif isinstance(elements, str):
            keys = self.sets[elements].selection

        else:
            keys = elements

        for key in keys:
            data[key] = rdict[field][key]

        return data

    # ==============================================================================
    # Summary
    # ==============================================================================

    def summary(self):
        """Prints a summary of the Structure object.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        print(self)

    # ==============================================================================
    # App
    # ==============================================================================

    def view(self, mode=''):
        """Starts the PyQt app for visualisation.

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

            from compas_fea.app.app import App

            app = App(structure=self, mode=mode)
            app.start()

        except Exception:
            print('***** Launching App failed *****')

    # ==============================================================================
    # Save
    # ==============================================================================

    def save_to_obj(self, output=True):
        """Exports the Structure object to an .obj file through Pickle.

        Parameters
        ----------
        output : bool
            Print terminal output.

        Returns
        -------
        None

        """

        filename = os.path.join(self.path, self.name + '.obj')

        with open(filename, 'wb') as f:
            pickle.dump(self, f)

        if output:
            print('***** Structure saved to: {0} *****\n'.format(filename))

    # ==============================================================================
    # Load
    # ==============================================================================

    @staticmethod
    def load_from_obj(filename, output=True):
        """Imports a Structure object from an .obj file through Pickle.

        Parameters
        ----------
        filename : str
            Path to load the Structure .obj from.
        output : bool
            Print terminal output.

        Returns
        -------
        obj
            Imported Structure object.

        """

        with open(filename, 'rb') as f:
            structure = pickle.load(f)

        if output:
            print('***** Structure loaded from: {0} *****'.format(filename))

        return structure
