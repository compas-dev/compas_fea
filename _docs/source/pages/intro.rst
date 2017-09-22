********************************************************************************
Introduction
********************************************************************************

Finite element analysis, or the finite element method, is a numerical approach to solving a variety of problems in the sciences, mathematics and engineering fields. In a broad sense, a continuum such as a fluid or solid volume, is discretised into a set of smaller discrete elements. For each element, data of interest, such as stresses, displacements, temperatures and so on, are found at the nodes and element integration points. They are interpolated for values across the element with shape functions. The greater the number of elements used to represent the continuum, the better the numerical model will represent the original continuous solution. The finite element method is often used, as closed-form solutions for the continua cases can be difficult or impossible to ascertain, and so a numerical approximation is sought.

.. image:: /_images/discretise-bone.png
   :scale: 65 %

.. image:: /_images/discretise-rim.png
   :scale: 28 %

Example discretisations into finite elements: Scientific Computing and Imaging Institute, University of Utah (left), COMSOL Multiphysics (right).

The compas_fea package of the compas framework seeks to aid the user, be they an architect, scientist or engineer, in creating and analysing a suitable finite element model for their problem. This is done by creating a **Structure** object, to contain geometric information about the model, and then to apply loads, displacements, materials and so forth for a subsequent analysis. This construction of the **Structure** object may be performed in a pure scripting manner with Python, and/or through various modules that help construct the object through present or parametrically generated geometry. Once the model has been constructed, it may be analysed through a finite element solver in the background, with the data then stored back into the original class and as raw data files. The data can then be post-processed to display the results either through standard compas viewers and applications, or with visualisation support from specific CAD or finite element software.

.. image:: /_images/mesh-floor_blender.png
   :scale: 50 %

A scripting and CAD software pairing can be used to create and analyse a structure and then visualise the results.

By using the compas_fea package, the majority of the repetitive scripting tasks needed to perform a geometrically or structurally complex analysis are eliminated, allowing for the rapid investigation of models, with easy to use and streamlined data post-processing and visualisation support.

Note, that although finite element analysis has established itself as the preferred analysis method in a variety of fields, it is important to construct a model that closely represents the physical problem. As such, the results of a finite element analysis should always be checked with hand calculations, intuition, experience, and ideally reviewed by someone skilled in the field before the results are taken as "correct".
