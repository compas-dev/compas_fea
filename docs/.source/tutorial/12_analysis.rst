********************************************************************************
Analysis
********************************************************************************

This page describes how to analyse a completed **Structure** object and view the resulting data. There are three processes involved when analysing a **Structure** object using a specific finite element software package or library:

* Write the native input file for the FE software with the method ``.write_input_file()``.

* Send the input file to the FE solver for analysis with method ``.analyse()``.

* Extract the data from the analysis results and return them back to **structure.results**. The relevant data are extracted with method ``.extract_data()``.

These three processes are performed in sequence using the method ``.analyse_and_extract()``, which takes the ``software`` string (``'abaqus'``, ``'ansys'`` or ``'opensees'``), a list of the data ``fields`` to extract, the number of processor cores to use with ``cpus`` (currently for Abaqus only and defaults to 4), and if needed some information on the ``license`` type (defaults to ``'research'``, a restricted ``'student'`` license is also accepted). A call to this method looks like:

.. code-block:: python

    mdl.analyse_and_extract(software='abaqus', fields=['u', 's'], cpus=4, license='research')

Some additional arguments that can be given to ``.analyse_and_extract()`` are: ``output`` (bool) to display terminal text updates, ``return_data`` (bool) to return results back to **structure.results** or not, ``components`` (list) to request individual components of the requested ``fields``, and ``dof`` (int) which is specific to OpenSees for the number of degrees-of-freedom at a node (3 or 6).


------
Abaqus
------

The input file for generating an Abaqus structural model is the ``.inp`` file. With this file, it is possible to generate and analyse a structural model, as well as request certain output data to be written to an output database ``.odb`` file. Because the official reference documentation for Abaqus ``.inp`` files is vast, it will not be described here what every line of the ``.inp`` file means. There are a few important points to highlight about the Python procedure and data format of the **Structure** object, and the generated input file format:

* Abaqus uses a numbering system that starts from 1, therefore for the input file every node and element from the **Structure** object has 1 added to it (as Python is 0 based), which is then subtracted for all results data so that it remains consistent with the input numbering system.

* When an element is created in the input file, **compas_fea** will also make an individual set for just that element named **element_x**, where **x** is the Python 0 based element number. Because of the different numbering systems of Python and Abaqus, an element set named **element_4** will refer to Abaqus element number 5.

When an input file is written, a confirmation message will appear (if ``output=True``) in the terminal stating where it was written to:

.. code-block:: python

    ***** Abaqus input file generated: C:/Temp/truss_tower.inp *****

The input file will be sent for analysis via Abaqus in a system subprocess that launches the Abaqus executable ``abaqus cae`` with no graphical user interface (``noGUI`` mode) and running the **launch_job.py** script from **compas_fea.fea.abaq**. The goal of this subprocess is to pair the Abaqus executable with the ``.inp`` file and to generate an ``.odb`` file of data, and is equivalent to manually performing the following in a terminal:

.. code-block:: bash

    abaqus cae noGUI=~/compas_fea/fea/abaq/launch_job.py -- arguments

During analysis (if ``output=True``), an information stream will print a rolling update of the subprocess progress, and show ``COMPLETED`` if the analysis was successful. If it was not possible to debug the issue from the terminal messages, the model should be inspected manually within Abaqus by loading the input file and submitting a job with the job monitor open. Student versions of Abaqus must have ``cpus=1`` (this is the case by default), as multi-core processing is not enabled for student versions. The output stream may look like the following:

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

If the analysis was successful and if ``output=True``, a confirmation message will appear in the terminal with the analysis time taken:

.. code-block:: python

    ***** Analysis successful *****

    ***** Abaqus analysis time : 17.1095 s *****

If the analysis was unsuccessful, the terminal will look similar to the following:

.. code-block:: python

    Abaqus/Analysis exited with errors
    Abaqus Error: cae exited with an error.

    ***** Analysis failed *****

If some, but not all data was written to the ``.odb`` file, the data extraction will still try to continue by reading the last frame of the output database. It must be remembered that if the analysis did not fully complete, this last frame is **NOT** the final frame of the analysis, and should be respected as an equilibrium state taking actions less than those applied. Often this frame will be at the stage that the given number of increments managed to progress to, and so increasing this number of ``increments`` in the **Step** may help the analysis continue further and reach the final equilibrium state.

The data are extracted from the output database ``.odb`` file with the ``abaq.extract_odb_data()`` function, which is called automatically as part of the ``.extract_data()`` method. In the same folder as the ``.odb`` file, it will generate a ``results.json`` file of scraped unprocessed data, based on what was given in ``fields`` and ``components``. This file will be in the folder **/path/name/** and will store the data back into the **Structure** object with the following confirmation (if ``output=True``):

.. code-block:: bash


    ***** Saving data to structure.results successful *****

    ***** Data extracted from Abaqus .odb file : 2.3439 s *****

If there was a problem with saving the data the following error message will appear:

.. code-block:: bash

    ***** Saving data to structure.results unsuccessful *****


--------
OpenSees
--------

The input file for generating an OpenSees structural model is the ``.tcl`` input file. A ``basic`` model type will be made in 3D ``-ndm 3`` with degrees-of-freedom at each node ``-ndf`` set from the ``dof`` argument. Nodes and elements will be numbered starting from 1, and then 1 subtracted for the storage of data after the analysis, so that it is consistent with the input **Structure** object. An important difference (currently) with OpenSees is that the structural model should have only two steps: the first step representing all of the persistent boundary conditions containing only **Displacement** objects, and the second step representing all applied **Load** objects and any further applied **Displacement** objects.

Beam elements must be given an ``ex`` local axis orientation for ``geomTransf``, as OpenSees will not make an assumption for the cross-section orientation. This should be defined either directly when adding the elements with the ``axes`` argument, or added to the element name (``{'ex': [0, 1, 0]}`` for example) so it can be picked-up in a CAD environment and automatically applied. This orientation need not be defined for **TrussElement** types as there is no local bending orientation.

When written, a confirmation message will appear in the terminal showing where the file was saved:

.. code-block:: python

    ***** OpenSees input file generated: C:/Temp/beam_frame.tcl *****

The input file will be sent for analysis via OpenSees in a system subprocess that launches the executable, given by the ``exe`` string, or by assuming the default ``C:/OpenSees.exe`` location for Windows. No graphical user interface is launched for OpenSees, feedback will only be presented in the terminal while the ``.tcl`` file is running:

.. code-block:: none

             OpenSees -- Open System For Earthquake Engineering Simulation
                  Pacific Earthquake Engineering Research Center
                         Version 2.5.0 (rev 6536) 64-Bit

        (c) Copyright 1999-2016 The Regents of the University of California
                                All Rights Reserved
   (Copyright and Disclaimer @ http://www.berkeley.edu/OpenSees/copyright.html)

Followed by a completion message after the analysis has successfully completed, or with terminal output stating any error messages that have arisen:

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

As OpenSees support is still in early development, only limited output is automatically extracted, mainly nodal data such as ``'u'``: displacements and ``'ur'``: rotations, ``rf``: reaction forces and ``rm``: reaction moments, and only limited element data such as truss axial forces and some beam element data. Data will be stored for all nodes and elements as ``.out`` text files such as ``step_name_u.out``. These files are organised with OpenSees file writing defaults, which lists analysis increments vertically in the output text files and the data horizontally. **Note**: plotting functions currently use only the final increment, i.e. the last line of the file.


-----
Ansys
-----

-


===========================
Fields, components and data
===========================

After the analysis, the data are stored in the **Structure** object, where they can be accessed by the user to read or visualise the results. The organisation of the collected data in ``structure.results`` is in nested dictionaries with keys following a sequence of: the ``step`` string for the **Step** of interest, a data type string for ``'nodal'`` or ``'element'`` based data, the ``field`` string corresponding to one of the field tables below, and finally the node or element number. The general format of accessing data is thus ``structure.results[step][type][field][number]``. Two helper methods are also provided through ``structure.get_nodal_results()`` and ``structure.get_element_results()``, where the ``step``, ``field`` and ``nodes`` or ``elements`` are given the same as above, and the requested results are returned as a dictionary:

.. code-block:: python

    mdl.get_nodal_results(step='step_load', field='rfm', nodes='nset_pins')

.. code-block:: python

    mdl.get_element_results(step='step_load', field='smises', elements=[10]

The ``field`` strings are based on the notation tables below for the nodal data and the element data:

-----------
Node fields
-----------

+-------------------------------+-----------+-----------+-----------+-----------+
| Field                         |     x     |     y     |     z     | Magnitude |
+===============================+===========+===========+===========+===========+
|``'rf'`` Reaction forces       | ``'rfx'`` | ``'rfy'`` | ``'rfz'`` | ``'rfm'`` |
+-------------------------------+-----------+-----------+-----------+-----------+
|``'rm'`` Reaction moments      | ``'rmx'`` | ``'rmy'`` | ``'rmz'`` | ``'rmm'`` |
+-------------------------------+-----------+-----------+-----------+-----------+
|``'u'``  Displacements         | ``'ux'``  | ``'uy'``  | ``'uz'``  | ``'um'``  |
+-------------------------------+-----------+-----------+-----------+-----------+
|``'ur'`` Rotations             | ``'urx'`` | ``'ury'`` | ``'urz'`` | ``'urm'`` |
+-------------------------------+-----------+-----------+-----------+-----------+
|``'cf'`` Concentrated forces   | ``'cfx'`` | ``'cfy'`` | ``'cfz'`` | ``'cfm'`` |
+-------------------------------+-----------+-----------+-----------+-----------+
|``'cm'`` Concentrated moments  | ``'cmx'`` | ``'cmy'`` | ``'cmz'`` | ``'cmm'`` |
+-------------------------------+-----------+-----------+-----------+-----------+

.. - ``'nt'``: nodal temperatures.

--------------
Element fields
--------------

For elements such as shell elements, the local element axes can be accessed through ``'axes'`` as a component entry. **Note**: shell forces and moments are per unit width.

+-----------------------------+---------------------------+---------------------------+---------------------------+
|``'spf'`` Spring forces      |``'spfx'``                 |``'spfy'``                 |``'spfz'``                 |
+-----------------------------+---------------------------+---------------------------+---------------------------+
|``'sf'``  Section forces     |``'sf1'`` Axial            |``'sf2'`` Shear `x`        |``'sf3'`` Shear `y`        |
+-----------------------------+---------------------------+---------------------------+---------------------------+
|``'sf'``  Shell forces       |``'sf1'`` Axial `x`        |``'sf2'`` Axial `y`        |``'sf3'`` Shear `y`        |
+-----------------------------+---------------------------+---------------------------+---------------------------+
|                             |``'sf4'`` Transverse `x`   |``'sf5'`` Transverse `y`   |                           |
+-----------------------------+---------------------------+---------------------------+---------------------------+
|``'sm'``  Section moments    |``'sm1'`` Moment `x-x`     |``'sm2'`` Moment `y-y`     |``'sm3'`` Torsion          |
+-----------------------------+---------------------------+---------------------------+---------------------------+
|``'sm'``  Shell moments      |``'sm1'`` Moment `y-y`     |``'sm2'`` Moment `x-x`     |``'sm3'`` Torsion          |
+-----------------------------+---------------------------+---------------------------+---------------------------+
|``'se'``  Section strains    |``'se1'`` Axial            |``'se2'`` Shear `y`        |``'se3'`` Shear `x`        |
+-----------------------------+---------------------------+---------------------------+---------------------------+
|``'sk'``  Section curvatures |``'skx'`` Curvature `x-x`  |``'sky'`` Curvature `y-y`  |``'skz'`` Twist            |
+-----------------------------+---------------------------+---------------------------+---------------------------+
|``'sk'``  Shell curvatures   |``'skx'`` Curvature `y-y`  |``'sky'`` Curvature `x-x`  |``'skz'`` Twist            |
+-----------------------------+---------------------------+---------------------------+---------------------------+
|``'s'``   Stress (beams)     |``'sxx'`` Axial            |``'syy'`` Hoop             |``'sxy'`` Torsion          |
+-----------------------------+---------------------------+---------------------------+---------------------------+
|``'s'``   Stress (shells)    |``'sxx'`` Axial            |``'syy'`` Axial            |``'sxy'`` Shear            |
+-----------------------------+---------------------------+---------------------------+---------------------------+
|``'s'``   Stress (derived)   |``'smises'`` Von Mises     |``'smaxp'`` Max principal  |``'sminp'`` Min principal  |
+-----------------------------+---------------------------+---------------------------+---------------------------+
|``'e'``   Strain (beams)     |``'exx'`` Axial            |``'eyy'`` Hoop             |``'exy'`` Shear (torsion)  |
+-----------------------------+---------------------------+---------------------------+---------------------------+
|``'e'``   Strain (shells)    |``'exx'`` Axial            |``'eyy'`` Axial            |``'exy'`` Shear            |
+-----------------------------+---------------------------+---------------------------+---------------------------+
|``'e'``   Strain (derived)   |``'emaxp'`` Max principal  |``'eminp'`` Min principal  |                           |
+-----------------------------+---------------------------+---------------------------+---------------------------+

Reinforcement forces ``'rbfor'``


------------------------------
Integration and section points
------------------------------

For ``'nodal'`` data, accessing the displacement in `z` for step ``'step_load'`` and for node 4 would be ``structure.results['step_load']['nodal']['uz'][4]``, which would give a single float value in return. For ``'element'`` data, there is often no single data value that can represent the entire element, as some elements require many data values to be evaluated across its volume, especially higher order elements, quads and solid elements. During a finite element analysis, specific points are evaluated across an element and  section related to the element shape function and cross-section shape (Gauss points). Each of these data-points is stored by **compas_fea** for each of the elements with an integration point--section point string key. This special key takes the form of ``'ip4_sp1'``, which represents data for integration point 4 and section point 1 (see the Elements and Sections topics for the locations of these points).

The data request ``structure.results['step_load']['element']['smises'][4]`` for an example element, will return a dictionary of data with string keys as the integration point--section point keys. For a four noded linear shell element, these would be four integration points (the four internal points, unless a reduced integration scheme is used leading to one point) and two section points (top and bottom layers by default). When data stored in this integration--section point format are converted to nodal data, which is important for plotting data on meshes where vertices are coloured, the following points must be observed:

- For some situations, taking a mean value of all data points for an element could give meaningless or misleading results. For example, the mean value of normal stresses in a beam under pure bending would be zero, as positive and negative normal stresses would cancel each other out.

- Selecting one representative integration point for an element is generally not possible without some understanding of the structural model and loading. For instance, points around a beam cross-section will have completely different stress values depending on the combination of major axis and minor axis bending.

- Picking a maximum value of Von Mises stress could be used to find a critical heavily stressed point, as these stresses are always positive. But picking a maximum or minimum value for a stress where the sign matters is not so straightforward and must be done carefully, because it represents say compression or tension.

