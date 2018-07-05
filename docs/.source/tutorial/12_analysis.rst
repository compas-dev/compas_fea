********************************************************************************
Analysis
********************************************************************************

This page describes how to analyse a completed **Structure** object and view the resulting data. There are three processes in analysing a **Structure** object when using a specific finite element software package or library:

* Write the native input file for the FE software to read with the method ``.write_input_file()``.

* Send the input file to the FE solver for analysis with method ``.analyse()``.

* Extract the data from the analysis results and store them back into **structure.results**. The relevant data are extracted with method ``.extract_data()``.

These three stages are performed in sequence using the method ``.analyse_and_extract()``, which takes the ``software`` string (``'abaqus'``, ``'ansys'``, ``'opensees'`` or ``sofistik``), a list of the data ``fields`` to extract, the number of processor cores to use with ``cpus`` (currently for Abaqus only), and if needed some information on the ``license`` type. A call to this method looks like:

.. code-block:: python

    mdl.analyse_and_extract(software='abaqus', fields=['u', 's'])


------
Abaqus
------

The input file for generating an Abaqus structural model is the ``.inp`` input file. With this file, it is possible to generate and analyse a structural model, as well as request certain output data to be written to an output database ``.odb`` file. Because the official reference documentation for Abaqus ``.inp`` files is vast, it will not be described here what every line of the ``.inp`` file means. There are a few important points to highlight about the Python procedure and data format of the **Structure** object, and the generated input file format: 1) Abaqus uses a numbering system that starts from 1, therefore for the input file every node and element from the **Structure** object has 1 added to it, which is then subtracted for all results data so that it remains consistent with the input numbering. 2) When an element is created in the input file, **compas_fea** may also make an individual set for just that element named **element_x**. Because of the different numbering systems of Python and Abaqus, an element set named **element_4** will refer to Abaqus element number 5.

When an input file is written, a confirmation message will appear in the terminal stating where it was written to:

.. code-block:: python

    ***** Abaqus input file generated: C:/Temp/truss_tower.inp *****

The input file will be sent for analysis via Abaqus in a Python subprocess that launches the Abaqus executable ``abaqus cae`` with no graphical user interface (``noGUI`` mode) and running the **launch_job.py** script from **compas_fea.fea.abaq**. The goal of this subprocess is to pair the Abaqus executable with the ``.inp`` file and to generate an ``.odb`` file of data, and is equivalent to manually performing the following in a terminal:

.. code-block:: bash

    abaqus cae noGUI=~/compas_fea/fea/abaq/launch_job.py -- arguments

During analysis, an information stream will print a rolling update of the subprocess progress, and show ``COMPLETED`` if the analysis was successful. If there was not a successful analysis, a variety of error messages will appear to try and help the user evaluate what may have gone wrong. If it was not possible to debug the issue from the terminal messages, the model should be inspected manually within Abaqus by loading the input file and submitting a job with the job monitor open. Student versions of Abaqus must have ``cpus=1`` (this is the case by default), as multi-core processing is not enabled for student versions. The output stream may look like the following:

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

If the analysis was successful, a confirmation message will appear in the terminal with the analysis time taken:

.. code-block:: python

    ***** Analysis successful *****

    ***** Abaqus analysis time : 17.1095 s *****

If the analysis was unsuccessful, the terminal will look similar to the following:

.. code-block:: python

    Abaqus/Analysis exited with errors
    Abaqus Error: cae exited with an error.

    ***** Analysis failed - attempting to read error logs *****

If this is the case, the script will attempt to read a variety of error logs that are made during the analysis. If some, but not all data, was written to the ``.odb`` file, the data extraction will still try to continue by reading the last frame of the output database. It must be remembered that if the analysis did not fully complete, this last frame is **NOT** the final frame of the analysis, and should be respected as an equilibrium state taking actions less than those applied. Often this frame will be at the stage that the given number of increments managed to progress to, and so increasing this number of increments may help the analysis continue further and reach the final equilibrium state.

.. To do, other common error messages and solution.

The data are extracted from the output database ``.odb`` file with the ``abaq.extract_odb_data()`` function, which is called automatically as part of the ``.extract_data()`` method. In the same folder as the ``.odb`` file, it will generate a ``results.json`` file of scraped unprocessed data. This file will be in the folder **/path/name/** and will store the data back into the **Structure** object with the following confirmation:

.. code-block:: bash


    ***** Saving data to structure.results successful *****

    ***** Data extracted from Abaqus .odb file : 2.3439 s *****

If there was a problem with saving the data the following error message will appear:

.. code-block:: bash

    ***** Saving data to structure.results unsuccessful *****


--------
OpenSees
--------

The input file for generating an OpenSees structural model is the ``.tcl`` input file. A ``basic`` model type will be made in 3D ``-ndm 3`` with all degrees-of-freedom at each node ``-ndf 6``, unless the model is exclusively made of truss elements where ``-ndf 3`` will instead be used. Nodes and elements will be numbered starting from 1, and then 1 subtracted for the storage of data after the analysis, so that it is consistent with the input **Structure** object. An important difference (currently) with OpenSees is that the structural model should have only two steps: the first step representing all of the persistent boundary conditions containing only **Displacement** objects, and the second step representing all applied **Load** objects and any further applied **Displacement** objects.

Beam elements must be given an ``ex`` local axis orientation for ``geomTransf``, as OpenSees will not make an assumption for the cross-section orientation. This should be defined either directly when adding the elements with the ``axes`` argument, or added to the element name (``{'ex': [0, 1, 0]}`` for example) so it can be picked-up in a CAD environment and automatically applied. This orientation need not be defined for **TrussElement** types as there is no local bending orientation.

When written, a confirmation message will appear in the terminal showing where the file was saved:

.. code-block:: python

    ***** OpenSees input file generated: C:/Temp/beam_frame.tcl *****

The input file will be sent for analysis via OpenSees in a Python subprocess that launches the executable, given by the ``exe`` string, or by assuming the default ``C:/OpenSees.exe`` location for Windows. No graphical user interface is launched for OpenSees, feedback will only be presented in the terminal while the ``.tcl`` file is running:

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

Only simple constant static loads are currently implemented with the following basic analysis settings:

    - ``constraints Transformation``.
    - ``numberer RCM``.
    - ``system ProfileSPD``.
    - ``test NormUnbalance`` based on the ``step.tolerance`` and ``step.iterations`` of the **Step** object.
    - ``algorithm NewtonLineSearch``.
    - ``integrator LoadControl``.
    - ``analysis Static`` and ``analyze`` using the number of increments in ``step.increments``.

As OpenSees support is still in early development, only limited output is automatically extracted, mainly nodal data such as ``'u'``: displacements and ``'ur'``: rotations, ``rf``: reaction forces and ``rm``: reaction moments, and only limited element data such as truss axial forces. Data will be stored for all nodes and elements as ``.out`` text files such as ``step_name_node_u.out``. These files are organised with OpenSees file writing defaults, which list analysis increments vertically and data horizontally. **Note**: plotting functions currently use only the final increment, i.e. the last line of the file.


--------
Sofistik
--------

The input file for generating a Sofistik structural model is the ``.dat`` input file. Sofistik differs from Abaqus and OpenSees for the layout of its code, in that lines of code must be supplied in the appropriate sub-program, such as **PROG AQUA**, **PROG SOFIMSHA** or **PROG SOFILOAD**. The input file code will be automatically wrapped with these sub-programs calls, but as a consequence of the way they need to be ordered, will produce an input file which differs significantly when compared to the layout of the ``.tcl`` and ``.inp`` files. Similar to Abaqus and OpenSees, nodes and elements will be added starting from number 1, different from the Python 0 based numbering. The nodes will also be internally re-ordered by Sofistik for optimising the analysis via ``CTRL OPT OPTI 10``. For every **ElementProperties** object, a Sofistik group will be made in multiples of 10000, such that element 2943 in group number 2 will have Sofistik element number 22943, as it will be associated with ``GRP 2 BASE 20000``.

When the ``.dat`` file is written, a confirmation message will appear in the terminal:

.. code-block:: python

    ***** Sofistik input file generated: C:/Temp/beam_frame.dat *****

Sofistik functionality is still in development and only supports writing the input ``.dat`` file with ``.write_input_file()``. It will currently not be automatically sent for analysis or data extracted (``.analyse()`` and ``.extract_data()`` do net yet do anything). The model must be manually run from the Sofistik GUI through **Execute** and then visualised in **WinGRAF**.


-----
Ansys
-----

-


===========================
Fields, components and data
===========================

After the analysis, the data are stored in the **Structure** object, where they can be accessed by the user to read or visualise the results. The organisation of the collected data in ``structure.results`` is in nested dictionaries with keys following a sequence of: the ``step`` string for the **Step** of interest, a data type string for ``'nodal'`` or ``'element'`` based data, the ``field`` string corresponding to the fields below, and finally the node or element number. The general format of accessing data is thus ``structure.results[step][type][field][number]``. A helper method is also provided through ``structure.get_nodal_results()`` and ``structure.get_element_results()``, where the ``step``, ``field`` and ``node`` or ``elements`` are given as above, and the requested results are returned as a dictionary:

.. code-block:: python

    mdl.get_nodal_results(step='step_load', field='rfm', nodes='nset_pins')

.. code-block:: python

    mdl.get_element_results(step='step_load', field='sxx', elements=[10]

The ``field`` strings are based on the notation below:

-----------
Node fields
-----------

+-------------------------------+-----------+-----------+-----------+-----------+
| Field                         |     x     |     y     |     z     | Magnitude |
+===============================+===========+===========+===========+===========+
| Reaction forces      ``'rf'`` | ``'rfx'`` | ``'rfy'`` | ``'rfz'`` | ``'rfm'`` |
+-------------------------------+-----------+-----------+-----------+-----------+
| Reaction moments     ``'rm'`` | ``'rmx'`` | ``'rmy'`` | ``'rmz'`` | ``'rmm'`` |
+-------------------------------+-----------+-----------+-----------+-----------+
| Displacements        ``'u'``  | ``'ux'``  | ``'uy'``  | ``'uz'``  | ``'um'``  |
+-------------------------------+-----------+-----------+-----------+-----------+
| Rotations            ``'ur'`` | ``'urx'`` | ``'ury'`` | ``'urz'`` | ``'urm'`` |
+-------------------------------+-----------+-----------+-----------+-----------+
| Concentrated forces  ``'cf'`` | ``'cfx'`` | ``'cfy'`` | ``'cfz'`` | ``'cfm'`` |
+-------------------------------+-----------+-----------+-----------+-----------+
| Concentrated moments ``'cm'`` | ``'cmx'`` | ``'cmy'`` | ``'cmz'`` | ``'cmm'`` |
+-------------------------------+-----------+-----------+-----------+-----------+

.. - ``'nt'``: nodal temperatures.

--------------
Element fields
--------------

For elements such as shell elements, the local element axes can be accessed through ``'axes'`` as a component entry. **Note**: shell forces and moments are per unit width.

+-----------------------------+---------------------------+---------------------------+---------------------------+
| Spring forces ``'spf'``     | ``'spfx'``                | ``'spfy'``                | ``'spfz'``                |
+-----------------------------+---------------------------+---------------------------+---------------------------+
| Section forces ``'sf'``     | Axial ``'sf1'``           | Shear `x` ``'sf2'``       | Shear `y` ``'sf3'``       |
+-----------------------------+---------------------------+---------------------------+---------------------------+
| Shell forces ``'sf'``       | Axial `x` ``'sf1'``       | Axial `y` ``'sf2'``       | Shear `y` ``'sf3'``       |
+-----------------------------+---------------------------+---------------------------+---------------------------+
|                             | Transverse `x` ``'sf4'``  | Transverse `y` ``'sf5'``  |                           |
+-----------------------------+---------------------------+---------------------------+---------------------------+
| Section moments ``'sm'``    | Moment `x-x` ``'smx'``    | Moment `y-y` ``'smy'``    | Torsion ``'smz'``         |
+-----------------------------+---------------------------+---------------------------+---------------------------+
| Shell moments ``'sm'``      | Moment `y-y` ``'smx'``    | Moment `x-x` ``'smy'``    | Torsion ``'smz'``         |
+-----------------------------+---------------------------+---------------------------+---------------------------+
| Section strains ``'se'``    | Axial ``'senx'``          | Shear `y` ``'sevy'``      | Shear `x` ``'sevx'``      |
+-----------------------------+---------------------------+---------------------------+---------------------------+
| Section curvatures ``'sk'`` | Curvature `x-x` ``'skx'`` | Curvature `y-y` ``'sky'`` | Twist ``'skz'``           |
+-----------------------------+---------------------------+---------------------------+---------------------------+
| Shell curvatures ``'sk'``   | Curvature `y-y` ``'skx'`` | Curvature `x-x` ``'sky'`` | Twist ``'skz'``           |
+-----------------------------+---------------------------+---------------------------+---------------------------+
| Stress ``'s'`` (beams)      | Axial ``'sxx'``           | Hoop ``'syy'``            | Torsion ``'sxy'``         |
+-----------------------------+---------------------------+---------------------------+---------------------------+
| Stress ``'s'`` (shells)     | Axial ``'sxx'``           | Axial ``'syy'``           | Shear ``'sxy'``           |
+-----------------------------+---------------------------+---------------------------+---------------------------+
| Stress (derived) ``'s'``    | Von Mises ``'smises'``    | Max principal ``'smaxp'`` | Min principal ``'sminp'`` |
+-----------------------------+---------------------------+---------------------------+---------------------------+
| Strain ``'e'`` (beams)      | Axial ``'exx'``           | Hoop ``'eyy'``            | Shear (torsion) ``'exy'`` |
+-----------------------------+---------------------------+---------------------------+---------------------------+
| Strain ``'e'`` (shells)     | Axial ``'exx'``           | Axial ``'eyy'``           | Shear ``'exy'``           |
+-----------------------------+---------------------------+---------------------------+---------------------------+
| Strain (derived) ``'e'``  ) | Max principal ``'emaxp'`` | Min principal ``'eminp'`` |                           |
+-----------------------------+---------------------------+---------------------------+---------------------------+

.. | Plastic strain ``'pe'`` (beams)             | Axial ``'pexx'``          | Axial ``'peyy'``          | Axial ``'pezz'`` | Shear ``'pexy'`` | Shear ``'pexz'`` | Shear ``'peyz'`` |

.. .. - ``'pe'`` derived (shells and beams): max principal plastc strain ``'pemaxp'`` and min principal plastic strain ``'peminp'``.
.. | Section strains ``'se'`` | Axial `x` ``'senx'``      | ``'SE2'`` axial `y`       | ``'SE3'`` shear      |
.. +--------------------------+---------------------------+---------------------------+----------------------+
.. |                          |``'SE4'`` transverse shear strain in `x`, ``'SE5'`` transverse shear strain in `y`, ``'SE6'`` through thickness strain.

Reinforcement forces ``'rbfor'``


------------------------------
Integration and section points
------------------------------

For ``'nodal'`` data, accessing the displacement in `z` for step ``'step_load'`` and for node 4 would be ``structure.results['step_load']['nodal']['uz'][4]``, which would give a single float value. For ``'element'`` data, there is often no single data value that can represent the entire element, as some elements require many data values to be evaluated across its volume, especially higher order elements. During a finite element analysis, specific points are evaluated across an element and  section related to the element shape function and cross-section shape (Gauss points). Each of these data-points is stored by **compas_fea** for each of the elements with an integration point--section point string key. This special key takes the form of ``'ip4_sp1'``, which represent data for integration point 4 and section point 1 (see the Elements and Sections topics for the locations of these points).

The data request ``structure.results['step_load']['element']['smises'][4]`` for an example shell element, will return a dictionary of data with string keys as the integration point--section point keys. For a four noded linear shell element, these would be four integration points (the four internal points, unless a reduced integration scheme is used leading to one point) and two section points (top and bottom layers by default). When data stored in this integration--section point format are converted to nodal data, which is important for plotting data on meshes where vertices are coloured, the following points must be observed:

- For some situations, taking a mean value of all data points for an element could give meaningless or misleading results. For example, the mean value of normal stresses in a beam under pure bending would be zero, as positive and negative normal stresses would cancel each other out.

- Selecting one representative integration point for an element is generally not possible without some understanding of the structural model and loading. For instance, points on a beam cross-section will have completely different stress values depending on the combination of major axis and minor axis bending.

- Picking a maximum value of Von Mises stress could be used to find a critical heavily stressed point, as these stresses are always positive. But picking a maximum or minimum value for a stress where the sign matters, because it represents say compression or tension, is not so straightforward and must be done carefully.

