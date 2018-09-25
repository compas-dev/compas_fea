
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


__author__    = ['Andrew Liew <liew@arch.ethz.ch>', 'Tomas Mendez <mendez@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'ObjectMixins',
]


class ObjectMixins(object):

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
                self.assign_element_property(element_property)
        else:
            element_properties.index = len(self.element_properties)
            self.element_properties[element_properties.name] = element_properties
            self.assign_element_property(element_properties)

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
