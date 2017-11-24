********************************************************************************
Analysis
********************************************************************************

This page describes how to analyse a completed **Structure** object and interpret the resulting data.

.. contents::


There are three steps in analysing a **Structure** object for a specific finite element software package or library:

* Write the required input file for the FE software.

* Send the input file to the FE solver for analysis.

* Extract the data from the analysis results and store in **structure.results**.

These three steps are performed in sequence with the method ``.analyse_and_extract()``, which takes the ``software`` string (``'abaqus'``, ``'ansys'``, ``'opensees'``), a list of the interested ``fields``, the number of processors to use ``cpus``, and if needed some information on the ``license`` type. A call to this method looks like:

.. code-block:: python

   mdl.analyse_and_extract(software='abaqus', fields=['u', 's'])


======================
Writing the input file
======================

The writing of the input file is done automatically when the ``.analyse_and_extract()`` method is called, which, in the background, calls the method ``.write_input_file()``. Below are a few key points about this input file, for the different ``software`` types.

------
Abaqus
------

The input file for generating an Abaqus structural model is the ``.inp`` input file. With this file, it is possible to generate and analyse a structural model, as well as request certain output data to be written to an output database ``.odb`` file. Because the official reference documentation for Abaqus ``.inp`` files is vast, it will not be described here what every line of the ``.inp`` file means. For users interested or experienced in Abaqus input file generation, see the Abaqus Documentation, particularly the Keywords Manual, which can be set-up during installation. There are a few important points to highlight about the Python procedure and data format of the **Structure** object, and the generated input file format:

- Abaqus uses a numbering system that starts from 1, therefore for the input file, every node and element from the **Structure** object has the number 1 added to it, which is then subtracted for all results data so that it remains consistent with the input.

- A node set **nset_all** is automatically generated containing all nodes of the **Structure**, as well as an element set **elset_all** for all elements, regardless of element type. Separate element sets for each element type are also automatically constructed, such as **elset_S4** for any four-noded shell elements.

- When making an exploded set, because of the different numbering systems of Python and Abaqus, an exploded  element set **element_4** will refer to Abaqus element 5.

When written, a confirmation message like below will appear in the terminal:

.. code-block:: python

   ***** Abaqus input file generated: C:/Temp/truss_tower.inp *****


==============
Model analysis
==============

When the ``.analyse_and_extract()`` method is called, and the input file has been written, the method ``.analyse()`` is called. Below are some of the details of what the different software types do when called for an analysis:

------
Abaqus
------

The input file will be sent for analysis via Abaqus in a Python subprocess that launches the Abaqus executable (``abaqus cae``) with no graphical user interface (``noGUI`` mode) and running the **launch_job.py** script. The purpose is to pair the Abaqus executable with the ``.inp`` file and to generate an ``.odb`` file of data, and is equivalent to manually performing the following in a terminal:

.. code-block:: bash

   abaqus cae noGUI=~/compas_fea/fea/abaq/odb.py -- arguments

During analysis, an information stream will print a rolling update of the subprocess progress, and show ``COMPLETED`` if the analysis was successful. If there was not a successful analysis, a variety of error messages will appear to try and help the user evaluate what may have gone wrong. If it was not possible to find what was wrong with the model from the terminal messages, the model should be inspected manually within Abaqus by loading the input file and submitting a job with the job monitor open.

.. code-block:: bash

   Abaqus JOB simple-truss
   Abaqus 6.14-1
   Begin Analysis Input File Processor
   13/09/2017 17:56:25
   Run pre.exe
   13/09/2017 17:56:28
   End Analysis Input File Processor
   Begin Abaqus/Standard Analysis
   13/09/2017 17:56:28
   Run standard.exe
   13/09/2017 17:56:30
   End Abaqus/Standard Analysis
   Abaqus JOB truss-tower COMPLETED

   Abaqus License Manager checked out the following licenses:
   Abaqus/Standard checked out 6 tokens from Flexnet server XXX-XXX-XXX.
   <212 out of 580 licenses remain available>.

If the analysis was successful, a confirmation message like below will appear in the terminal:

.. code-block:: python

   ***** Analysis successful *****

   ***** Abaqus analysis time : 17.1095 s *****

Note: If the analysis is unsuccessful, the terminal will look similar to the following:

.. code-block:: python

   Abaqus/Analysis exited with errors
   Abaqus Error: cae exited with an error.

   ***** Analysis failed - attempting to read error logs *****

If this is the case, the data extraction will still continue, reading the last frame of the output database file. It will then plot the results (if possible) to help identify what may have gone wrong in the model. This frame is NOT the final frame, and should be respected as an equilibrium state taking actions less than those applied. Often this frame will be at the stage that the given number of increments managed to progress with, and so increasing this increments number may help reach the final state.

To do, other common error messages and solution.


===============
Extracting data
===============

Finally, when the ``.analyse_and_extract()`` method is called and the analysis has completed, the relevant data is extracted with method ``.extract_data()``. Below are some of the details of what the different software types do when called for data extraction:

------
Abaqus
------

The data are extracted from the output database ``.odb`` file with the function ``abaq.extract_odb_data()``, which is called automatically as part of ``.extract_data()``. In the same folder as the ``.odb`` file, it will generate a ``results.json`` file of scraped unprocessed data. This file will be in the folder **/path/name/**, and which written, will store the data back into the **Structure** object with the following confirmation:

.. code-block:: bash


   ***** Saving data to structure.results successful *****

   ***** Data extracted from Abaqus .odb file : 2.3439 s *****

If there was a problem with saving the data the following error will occur:

.. code-block:: bash

   ***** Saving data to structure.results unsuccessful *****


===========================
Fields, components and data
===========================

After the analysis, the data are stored in the **Structure** object, where they are accessed by the user to read or visualise the results. The organisation of the collected data in ``structure.results`` is in nested dictionaries with keys following a pattern of the: ``step`` string, data type string (``'nodal'`` or ``'element'``), ``field`` string, and the node or element number string (``structure.results[step][type][field][number]``). The ``field`` strings are based on the notation below:

-----------
Node fields
-----------

- ``'rf'``: reaction forces ``'rfx'``, ``'rfy'``, ``'rfz'`` and magnitude ``'rfm'``.

- ``'rm'``: reaction moments ``'rmx'``, ``'rmy'``, ``'rmz'`` and magnitude ``'rmm'``.

- ``'u'``: displacements ``'ux'``, ``'uy'``, ``'uz'`` and magnitude ``'um'``.

- ``'ur'``: rotations ``'urx'``, ``'ury'``, ``'urz'`` and magnitude ``'urm'``.

- ``'cf'``: concentrated forces ``'cfx'``, ``'cfy'``, ``'cfz'`` and magnitude ``'cfm'``.

- ``'cm'``: concentrated moments ``'cmx'``, ``'cmy'``, ``'cmz'`` and magnitude ``'cmm'``.

- ``'nt'``: nodal temperatures.

--------------
Element fields
--------------

- ``'sf'`` (beams): section forces, axial force in ``'sfnx'`` , shear force `x` ``'sfvx'`` and shear force `y` ``'sfvy'``.

.. - ``'sf'`` (shells): section forces per width, axial force in `x` ``'sfnx'``, shear force `x` ``'sfvx'``, shear force `y` ``'sfvy'``, transverse shear force `x` ``'sfwx'`` and transverse shear force `y` ``'sfwy'``.

- ``'sm'`` (beams): section moments, bending moment about `x` ``'smx'``, bending moment about `y` ``'smy'`` and torsion moment ``'smz'``.

- ``'sm'`` (shells): section moments per width, bending moment about `y` ``'smx'``, bending moment about `x` ``'smy'`` and torsion moment ``'smz'``.

- ``'se'`` (beams): section strains, axial strain ``'senx'``, shear strain in `y` ``'sevy'`` and shear strain in `x` ``'sevx'``.

.. - ``'se'`` (shells): section strains, axial strain in `x` ``'senx'``, ``'SE2'`` axial strain in `y`, ``'SE3'`` shear strain, ``'SE4'`` transverse shear strain in `x`, ``'SE5'`` transverse shear strain in `y`, ``'SE6'`` through thickness strain.

- ``'sk'`` (beams): section curvatures, curvature about `x` ``'skx'`` , curvature about `y` ``'sky'`` and twist ``'skz'``.

- ``'sk'`` (shells): section curvatures, curvature about `y` ``'skx'``, curvature about `x` ``'sky'`` and twist ``'skz'``.

- ``'s'`` basic (beams): axial stress ``'sxx'``, hoop stress ``'syy'`` and shear stresse (torsion) ``'sxy'``.

- ``'s'`` basic (shells): axial stresses ``'sxx'`` ``'syy'`` and shear stress ``'sxy'``.

- ``'s'`` derived (shells and beams): Von Mises stress ``'smises'``, max principal stress ``'smaxp'`` and min principal stress ``'sminp'``.

- ``'e'`` basic (beams): axial strain ``'exx'``, hoop strain ``'eyy'`` and shear strain (torsion) ``'exy'``.

- ``'e'`` basic (shells): axial strains ``'exx'`` ``'eyy'`` and shear strain ``'exy'``.

- ``'e'`` derived (shells and beams): max principal strain ``'emaxp'`` and min principal strain ``'eminp'``.

.. - ``'pe'`` basic (beams): plastic axial strains ``'pexx'``, ``'peyy'``, ``'pezz'``  and plastic shear strains ``'pexy'``. ``'pexz'``, ``'peyz'``.

.. - ``'pe'`` derived (shells and beams): max principal plastc strain ``'pemaxp'`` and min principal plastic strain ``'peminp'``.

- ``'rbfor'``: reinforcement forces.

.. - For elements such as shell elements, the local element axes can be accessed through ``'axes'`` as a component entry.

------------------------------
Integration and section points
------------------------------

For ``'nodal'`` data, accessing the displacement in `z`, for step ``'step_load'``, and for node 4 would be ``structure.results['step_load']['nodal']['uz'][4]``, which would give a single float value. For ``'element'`` data, there is no single data value that can represent the entire element, as each element has physical dimensions and requires many data values across its volume. During a finite element analysis, specific points are evaluated across an element and  section related to the element shape function and cross-section shape (Gauss points). Each of these data-points is stored for the element as an integration point--section point string key. This key looks  like ``'ip4_sp1'``, which would be the data for integration point 4 and section point 1 (see the Elements and Sections topics for the locations of these points).

The data request ``structure.results['step_load']['element']['smises'][4]``, will, for an example shell element, return a dictionary of data with keys as the integration point--section point keys. For a four noded shell element these would be four integration points (the four internal points, unless a reduced integration scheme is used leading to one point) and two section points (top and bottom layers by default). When data stored in this format are converted to nodal data, the following points must be observed:

- Taking a mean value of all points could give meaningless or misleading results, for example, the mean value of normal stresses in a beam under pure bending would be zero, as positive and negative normal stresses would cancel each other out.

- Selecting one representative integration point is not possible without some understanding of the structural model and loading. For instance, any given point of a beam section will have completely different stress values depending on the degree of major axis or minor axis bending.

- Picking a maximum value of Von Mises stress could be used to find a critical heavily stressed point, as these stresses are always positive. But picking a maximum or minimum value for a stress where the sign matters, as with  compression or tension, is not so straightforward.

