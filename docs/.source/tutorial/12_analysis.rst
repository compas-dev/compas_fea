********************************************************************************
Analysis
********************************************************************************

This page describes how to analyse a complete **Structure** object and interpret the resulting data. There are three processes in analysing a **Structure** object using a specific finite element software package or library:

* Write the required input file for the FE software to read. This is done through the method ``.write_input_file()``.

* Send the input file to the FE solver for analysis through method ``.analyse()``.

* Extract the data from the analysis results and store in them back into **structure.results**. The relevant data are extracted with method ``.extract_data()``.

These three parts are performed in sequence using the method ``.analyse_and_extract()``, which takes the ``software`` string (``'abaqus'``, ``'ansys'``, ``'opensees'`` or ``sofistik``), a list of the data ``fields`` to extract, the number of processor cores to use ``cpus``, and if needed some information on the ``license`` type. A call to this method looks like:

.. code-block:: python

    mdl.analyse_and_extract(software='abaqus', fields=['u', 's'])


------
Abaqus
------

The input file for generating an Abaqus structural model is the ``.inp`` input file. With this file, it is possible to generate and analyse a structural model, as well as request certain output data to be written to an output database ``.odb`` file. Because the official reference documentation for Abaqus ``.inp`` files is vast, it will not be described here what every line of the ``.inp`` file means. There are a few important points to highlight about the Python procedure and data format of the **Structure** object, and the generated input file format: 1) Abaqus uses a numbering system that starts from 1, therefore for the input file every node and element from the **Structure** object has 1 added to it, which is then subtracted for all results data so that it remains consistent with the input numbering. 2) When an element is created, it also makes an individual set for just that element named **element_x**. Because of the different numbering systems of Python and Abaqus, an element set **element_4** will refer to Abaqus element 5.

When an input file is written, a confirmation message will appear in the terminal:

.. code-block:: python

    ***** Abaqus input file generated: C:/Temp/truss_tower.inp *****

The input file will be sent for analysis via Abaqus in a Python subprocess that launches the Abaqus executable ``abaqus cae`` with no graphical user interface (``noGUI`` mode) and running the **launch_job.py** script. The goal is to pair the Abaqus executable with the ``.inp`` file and to generate an ``.odb`` file of data, and is equivalent to manually performing the following in a terminal:

.. code-block:: bash

    abaqus cae noGUI=~/compas_fea/fea/abaq/launch_job.py -- arguments

During analysis, an information stream will print a rolling update of the subprocess progress, and show ``COMPLETED`` if the analysis was successful. If there was not a successful analysis, a variety of error messages will appear to try and help the user evaluate what may have gone wrong. If it was not possible to find what was wrong with the model from the terminal messages, the model should be inspected manually within Abaqus by loading the input file and submitting a job with the job monitor open. Student versions of Abaqus must have ``cpus=1`` (also by default), as multi-core processing is not enabled for these versions.

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

If the analysis was successful, a confirmation message will appear in the terminal:

.. code-block:: python

    ***** Analysis successful *****

    ***** Abaqus analysis time : 17.1095 s *****

**Note**: If the analysis was unsuccessful, the terminal will look similar to the following:

.. code-block:: python

    Abaqus/Analysis exited with errors
    Abaqus Error: cae exited with an error.

    ***** Analysis failed - attempting to read error logs *****

If this is the case, the script will attempt to read a variety of error logs that are made during the analysis. If some, but not all data, was written to the ``.odb`` file, the data extraction will still continue by reading the last frame of the output database. But it must be remembered that if the analysis did not fully complete, this last frame is **NOT** the final frame of the analysis, and should be respected as an equilibrium state taking actions less than those applied. Often this frame will be at the stage that the given number of increments managed to progress, and so increasing this number of increments number may help reach the final state.

.. To do, other common error messages and solution.

The data are extracted from the output database ``.odb`` file with ``abaq.extract_odb_data()``, which is called automatically as part of the ``.extract_data()`` method. In the same folder as the ``.odb`` file, it will generate a ``results.json`` file of scraped unprocessed data. This file will be in the folder **/path/name/** and will store the data back into the **Structure** object with the following confirmation:

.. code-block:: bash


    ***** Saving data to structure.results successful *****

    ***** Data extracted from Abaqus .odb file : 2.3439 s *****

If there was a problem with saving the data the following error message will appear:

.. code-block:: bash

    ***** Saving data to structure.results unsuccessful *****


--------
OpenSees
--------

The input file for generating an OpenSees structural model is the ``.tcl`` input file. A ``basic`` model type will be made in 3D ``-ndm 3`` with all degrees-of-freedom at each node ``-ndf 6``, unless the model is exclusively made of truss elements where ``-ndf 3`` will be used. Nodes and elements will be numbered starting from 1, and then 1 subtracted for the storage of data after the analysis, so that it is consistent with the input **Structure** object. An important difference (currently) with OpenSees is that the structural model should have only two steps: the first step representing all of the boundary conditions containing only **Displacement** objects, and the second step representing all applied **Load** objects.

Beam elements must be given an ``ex`` local axis orientation for ``geomTransf``, as OpenSees will not make an assumption for the cross-section orientation. This should be defined either directly when adding the elements with ``axes``, or added to the element name (``{'ex': [0, 1, 0]}`` for example) so it can be picked-up in a CAD environment. This orientation need not be defined for **TrussElement** types.

When written, a confirmation message will appear in the terminal:

.. code-block:: python

    ***** OpenSees input file generated: C:/Temp/beam_frame.tcl *****

The input file will be sent for analysis via OpenSees in a Python subprocess that launches the executable, given by the ``exe`` string, or by assuming by default ``C:/OpenSees.exe`` for Windows. No graphical user interface is launched, feedback will only be presented in the terminal while the ``.tcl`` file is running:

.. code-block:: none

             OpenSees -- Open System For Earthquake Engineering Simulation
                  Pacific Earthquake Engineering Research Center
                         Version 2.5.0 (rev 6536) 64-Bit

        (c) Copyright 1999-2016 The Regents of the University of California
                                All Rights Reserved
   (Copyright and Disclaimer @ http://www.berkeley.edu/OpenSees/copyright.html)

Followed by a completion message after the analysis:

.. code-block:: python

    ***** OpenSees analysis time : 0.9063 s *****

Only simple constant static loads are currently implemented with basic analysis settings: ``constraints Plain``, ``numberer RCM``, ``system ProfileSPD``, ``test NormUnbalance`` based on the ``step.tolerance`` and ``step.iterations``, ``algorithm NewtonLineSearch``, ``integrator LoadControl``, ``analysis Static`` and ``analyze`` using the number of increments in ``step.increments``.

As OpenSees support is still in development, only limited output is currently implemented (``'u'``: displacements and ``'ur'``: rotations, ``rf``: reaction forces and ``rm``: reaction moments). Data will be stored for all nodes and elements as ``.out`` text files such as ``step_name_node_u.out``. These files are organised with OpenSees defaults, which list analysis increments vertically and data horizontally. **Note**: plotting functions currently use only the final increment, i.e. the last line of the file.


--------
Sofistik
--------

The input file for generating a Sofistik structural model is the ``.dat`` input file. Sofistik differs from Abaqus and OpenSees in that lines of code must be supplied in the appropriate sub-program, such as **PROG AQUA**, **PROG SOFIMSHA** or **PROG SOFILOAD**. The input file code will be automatically wrapped with these sub-programs calls, but as a consequence of the way they need to be ordered, will produce an input file which differs significantly when compared to the layout of the ``.tcl`` and ``.inp`` files. Similar to Abaqus and OpenSees, nodes and elements will be added starting from number 1, but will be internally re-ordered by Sofistik for optimising the analysis via ``CTRL OPT OPTI 10`` For every **ElementProperties** object, a Sofistik group will be made in multiples of 10000, such that element 2943 in group 2 will have element number 22943 as it will be associated with ``GRP 2 BASE 20000``.

When written, a confirmation message will appear in the terminal:

.. code-block:: python

    ***** Sofistik input file generated: C:/Temp/beam_frame.dat *****

The input ``.dat`` file will currently not be automatically sent for analysis, it must be manually run from the Sofistik GUI through **Execute** and then visualised in **WinGRAF**.


-----
Ansys
-----

-


===========================
Fields, components and data
===========================

After the analysis, the data are stored in the **Structure** object, where they are accessed by the user to read or visualise the results. The organisation of the collected data in ``structure.results`` is in nested dictionaries with keys following a pattern of the: ``step`` string, data type string (``'nodal'`` or ``'element'``), the ``field`` string, and the node or element number (``structure.results[step][type][field][number]``). A helper method is also provided through ``structure.get_nodal_results()`` and ``structure.get_element_results()``, where the ``step``, ``field`` and ``node`` or ``elements`` are given, and the requested results returned:

.. code-block:: python

    mdl.get_nodal_results(step='step_load', field='rfm', nodes='nset_pins')

.. code-block:: python

    mdl.get_element_results(step='step_load', field='sxx', elements=[10]

The ``field`` strings are based on the notation below:

-----------
Node fields
-----------

| Field | x | y | z | Magnitude |
| --- | --- | --- | --- | --- |
| Reaction forces      ``'rf'`` | ``'rfx'`` | ``'rfy'`` | ``'rfz'`` | ``'rfm'`` |
| Reaction moments     ``'rm'`` | ``'rmx'`` | ``'rmy'`` | ``'rmz'`` | ``'rmm'`` |
| Displacements        ``'u'``  | ``'ux'``  | ``'uy'``  | ``'uz'``  | ``'um'``  |
| Rotations            ``'ur'`` | ``'urx'`` | ``'ury'`` | ``'urz'`` | ``'urm'`` |
| Concentrated forces  ``'cf'`` | ``'cfx'`` | ``'cfy'`` | ``'cfz'`` | ``'cfm'`` |
| Concentrated moments ``'cm'`` | ``'cmx'`` | ``'cmy'`` | ``'cmz'`` | ``'cmm'`` |
.. - ``'nt'``: nodal temperatures.

--------------
Element fields
--------------

| --- | --- | --- | --- | --- |
| Spring forces ``'spf'``                     | ``'spfx'``                | ``'spfy'``             | ``'spfz'``           |
| Section forces ``'sf'`` (beams)             | Axial ``'sfnx'``          | Shear `x` ``'sfvx'``   | Shear `y` ``'sfvy'`` |
| Section forces per width ``'sf'`` (shells)  | Axial `x` ``'sfnx'``      | Shear `x` ``'sfvx'``   | Shear `y` ``'sfvy'`` | Transverse shear `x` ``'sfwx'`` | Transverse shear `y` ``'sfwy'`` |
| Section moments ``'sm'`` (beams)            | Moment `x-x` ``'smx'``    | Moment `y-y` ``'smy'`` | Torsion ``'smz'``    |
| Section moments per width ``'sm'`` (shells) | Moment `y-y` ``'smx'``    | Moment `x-x` ``'smy'`` | Torsion ``'smz'`` |
| Section strains ``'se'`` (beams)            | Axial ``'senx'``          | Shear `y` ``'sevy'``   | Shear `x` ``'sevx'`` |
.. | Section strains ``'se'`` (shells)           | Axial `x` ``'senx'``   | , ``'SE2'`` axial strain in `y`, ``'SE3'`` shear strain, ``'SE4'`` transverse shear strain in `x`, ``'SE5'`` transverse shear strain in `y`, ``'SE6'`` through thickness strain.

| Section curvatures ``'sk'`` (beams)         | Curvature `x-x` ``'skx'`` | Curvature `y-y` ``'sky'`` | Twist ``'skz'`` |
| Section curvatures ``'sk'`` (shells)        | Curvature `y-y` ``'skx'`` | Curvature `x-x` ``'sky'`` | Twist ``'skz'`` |
| Stress ``'s'`` (beams)                      | Axial ``'sxx'``           | Hoop ``'syy'``            | Shear (torsion) ``'sxy'`` |
| Stress ``'s'`` (shells)                     | Axial ``'sxx'``           | Axial ``'syy'``           | Shear ``'sxy'`` |
| Stress (derived) ``'s'`` (shells and beams) | Von Mises ``'smises'``    | Max principal ``'smaxp'`` | Min principal ``'sminp'`` |
| Strain ``'e'`` (beams)                      | Axial ``'exx'``           | Hoop ``'eyy'``            | Shear (torsion) ``'exy'`` |
| Strain ``'e'`` (shells)                     | Axial ``'exx'``           | Axial ``'eyy'``           | Shear ``'exy'`` |
| Strain (derived) ``'e'`` (shells and beams) | Max principal ``'emaxp'`` | Min principal ``'eminp'`` |
.. | Plastic strain ``'pe'`` (beams)             | Axial ``'pexx'``          | Axial ``'peyy'``          | Axial ``'pezz'`` | Shear ``'pexy'`` | Shear ``'pexz'`` | Shear ``'peyz'`` |

.. .. - ``'pe'`` derived (shells and beams): max principal plastc strain ``'pemaxp'`` and min principal plastic strain ``'peminp'``.

Reinforcement forces ``'rbfor'``

.. - For elements such as shell elements, the local element axes can be accessed through ``'axes'`` as a component entry.


------------------------------
Integration and section points
------------------------------

For ``'nodal'`` data, accessing the displacement in `z` for step ``'step_load'`` and for node 4 would be ``structure.results['step_load']['nodal']['uz'][4]``, which would give a single float value. For ``'element'`` data, there is often no single data value that can represent the entire element, as some elements require many data values to be evaluated across its volume. During a finite element analysis, specific points are evaluated across an element and  section related to the element shape function and cross-section shape (Gauss points). Each of these data-points is stored for the element as an integration point--section point string key. This key looks  like ``'ip4_sp1'``, which would be the data for integration point 4 and section point 1 (see the Elements and Sections topics for the locations of these points).

The data request ``structure.results['step_load']['element']['smises'][4]`` for an example shell element, will return a dictionary of data with keys as the integration point--section point keys. For a four noded shell element these would be four integration points (the four internal points, unless a reduced integration scheme is used leading to one point) and two section points (top and bottom layers by default). When data stored in this format are converted to nodal data (which happens during the plotting data process), the following points must be observed:

- For some situations, taking a mean value of all points could give meaningless or misleading results. For example, the mean value of normal stresses in a beam under pure bending would be zero, as positive and negative normal stresses would cancel each other out.

- Selecting one representative integration point is generally not possible without some understanding of the structural model and loading. For instance, points on a beam cross-section will have completely different stress values depending on the combination of major axis and minor axis bending.

- Picking a maximum value of Von Mises stress could be used to find a critical heavily stressed point, as these stresses are always positive. But picking a maximum or minimum value for a stress where the sign matters, as with  compression or tension, is not so straightforward.

