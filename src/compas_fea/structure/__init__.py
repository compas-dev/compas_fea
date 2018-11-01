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


constraint
==========

.. currentmodule:: compas_fea.structure.constraint

:mod:`compas_fea.structure.constraint`

.. autosummary::
    :toctree: generated/

    Constraint
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


node
====

.. currentmodule:: compas_fea.structure.node

:mod:`compas_fea.structure.node`

.. autosummary::
    :toctree: generated/

    Node


set
===

.. currentmodule:: compas_fea.structure.set

:mod:`compas_fea.structure.set`

.. autosummary::
    :toctree: generated/

    Set


element
=======

.. currentmodule:: compas_fea.structure.element

:mod:`compas_fea.structure.element`

.. autosummary::
    :toctree: generated/

    Element
    BeamElement
    SpringElement
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


load
====

.. currentmodule:: compas_fea.structure.load

:mod:`compas_fea.structure.load`

.. autosummary::
    :toctree: generated/

    Load
    PrestressLoad
    PointLoad
    PointLoads
    LineLoad
    AreaLoad
    GravityLoad
    TributaryLoad
    HarmonicPointLoad


material
========

.. currentmodule:: compas_fea.structure.material

:mod:`compas_fea.structure.material`

.. autosummary::
    :toctree: generated/

    Material
    Concrete
    ConcreteSmearedCrack
    ConcreteDamagedPlasticity
    Stiff
    ElasticIsotropic
    ElasticOrthotropic
    ElasticPlastic
    Steel


misc
====

.. currentmodule:: compas_fea.structure.misc

:mod:`compas_fea.structure.misc`

.. autosummary::
    :toctree: generated/

    Misc
    Amplitude
    Temperatures


section
=======

.. currentmodule:: compas_fea.structure.section

:mod:`compas_fea.structure.section`

.. autosummary::
    :toctree: generated/

    Section
    AngleSection
    BoxSection
    CircularSection
    GeneralSection
    ISection
    PipeSection
    RectangularSection
    ShellSection
    MembraneSection
    SolidSection
    TrapezoidalSection
    TrussSection
    StrutSection
    TieSection
    SpringSection


step
====

.. currentmodule:: compas_fea.structure.step

:mod:`compas_fea.structure.step`

.. autosummary::
    :toctree: generated/

    Step
    GeneralStep
    ModalStep
    HarmonicStep
    BucklingStep


"""

from .constraint import *
from .displacement import *
from .element import *
from .element_properties import *
from .interaction import *
from .load import *
from .material import *
from .misc import *
from .node import *
from .section import *
from .step import *
from .structure import *
