"""
.. _compas_fea.structure:

********************************************************************************
structure
********************************************************************************

.. module:: compas_fea.structure


structure
=========

.. currentmodule:: compas_fea.structure.structure

:mod:`compas_fea.structure.structure`

.. autosummary::
    :toctree: generated/

    Structure
    load_from_obj


constraint
==========

.. currentmodule:: compas_fea.structure.constraint

:mod:`compas_fea.structure.constraint`

.. autosummary::
    :toctree: generated/

    TieConstraint


displacement
============

.. currentmodule:: compas_fea.structure.displacement

:mod:`compas_fea.structure.displacement`

.. autosummary::
    :toctree: generated/

    GeneralDisplacement
    FixedDisplacement
    PinnedDisplacement
    FixedDisplacementXX
    FixedDisplacementYY
    FixedDisplacementZZ
    RollerDisplacementX
    RollerDisplacementY
    RollerDisplacementZ
    RollerDisplacementXY
    RollerDisplacementYZ
    RollerDisplacementXZ


element
=======

.. currentmodule:: compas_fea.structure.element

:mod:`compas_fea.structure.element`

.. autosummary::
    :toctree: generated/

    Element
    BeamElement
    TrussElement
    StrutElement
    TieElement
    ShellElement
    MembraneElement
    SolidElement
    PentahedronElement
    TetrahedronElement
    HexahedronElement


element_properties
==================

.. currentmodule:: compas_fea.structure.element_properties

:mod:`compas_fea.structure.element_properties`

.. autosummary::
    :toctree: generated/

    ElementProperties


interaction
===========

.. currentmodule:: compas_fea.structure.interaction

:mod:`compas_fea.structure.interaction`

.. autosummary::
    :toctree: generated/

    HeatTransfer


load
====

.. currentmodule:: compas_fea.structure.load

:mod:`compas_fea.structure.load`

.. autosummary::
    :toctree: generated/

    Load
    PrestressLoad
    PointLoad
    LineLoad
    AreaLoad
    BodyLoad
    GravityLoad
    AcousticLoad
    TributaryLoad


material
========

.. currentmodule:: compas_fea.structure.material

:mod:`compas_fea.structure.material`

.. autosummary::
    :toctree: generated/

    Concrete
    ConcreteSmearedCrack
    ConcreteDamagedPlasticity
    ElasticIsotropic
    ElasticOrthotropic
    ElasticPlastic
    ThermalMaterial
    Steel


misc
====

.. currentmodule:: compas_fea.structure.misc

:mod:`compas_fea.structure.misc`

.. autosummary::
    :toctree: generated/

    Amplitude
    Temperature


section
=======

.. currentmodule:: compas_fea.structure.section

:mod:`compas_fea.structure.section`

.. autosummary::
    :toctree: generated/

    AngleSection
    BoxSection
    CircularSection
    GeneralSection
    ISection
    PipeSection
    RectangularSection
    ShellSection
    SolidSection
    TrapezoidalSection
    TrussSection
    StrutSection
    TieSection


step
====

.. currentmodule:: compas_fea.structure.step

:mod:`compas_fea.structure.step`

.. autosummary::
    :toctree: generated/

    GeneralStep
    HeatStep
    ModalStep
    HarmonicStep


"""

from .constraint import *
from .displacement import *
from .element import *
from .element_properties import *
from .interaction import *
from .load import *
from .material import *
from .misc import *
from .section import *
from .step import *
from .structure import *
