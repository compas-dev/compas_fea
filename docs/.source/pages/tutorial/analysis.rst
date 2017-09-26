.. _tutorial:

********************************************************************************
Analysis
********************************************************************************

This page describes how to analyse a completed **Structure** object and interpret the resulting data.

.. contents::


======
Abaqus
======

-----------------------
Generation of .inp file
-----------------------

The most important file in generating an Abaqus structural model is the ``.inp`` input file. With this file, it is possible to generate and analyse a structural model, as well as request certain output data to be written to an output database ``.odb`` file. The function that generates an input file from a **Structure** object is ``inp_generate()`` from the **compas_fea.fea.abaq.abaq** module (this module was not named **abaqus** as it would clash with an already present and  important import from Abaqus). To use the ``inp_generate()`` function, provide the ``structure`` object and the ``filename`` string of where to save the ``.inp`` file, and a confirmation that the file has been made will be given upon generation.

.. code-block:: python

   from compas_fea.fea.abaq import abaq

   >>> abaq.inp_generate(structure=mdl, filename='/home/al/Temp/simple-truss.inp')
   ***** Abaqus input file generated: /home/al/Temp/simple-truss.inp *****

Because the official reference documentation for Abaqus ``.inp`` files is vast, it will not be described here what every line of the ``.inp`` file means. For users interested or experienced in Abaqus input file generation, see the Abaqus Documentation, particularly the Keywords Manual, which can be set-up during installation. To see precisely how the **Structure** object data is converted into the ``.inp`` file format, see the functions ``inp_constraints()``, ``inp_elements()``, ``inp_heading()``, ``inp_materials()``, ``inp_misc()``, ``inp_nodes()``, ``inp_properties()``, ``inp_sets()``, ``inp_steps()`` of the **abaq** module.

There are a few important points to highlight about the Python procedure and data format of the **Structure** object, and the generated input file format:

- Abaqus uses a numbering system that starts from 1, therefore for the input file, every node and element from the **Structure** object has the number 1 added to it, which is then subtracted for all results data so that it remains consistent with the input.

- A node set **nset_all** is automatically generated containing all nodes of the **Structure**, as well as an element set **elset_all** for all elements, regardless of element type. Separate element sets for each element type are also automatically constructed, such as **elset_S4** for any four-noded shell elements.

- When making an exploded set, because of the different numbering systems of Python and Abaqus, an exploded  element set **element_4** will refer to Abaqus element 5.

-----------------
From .inp to .odb
-----------------

By using the ``.analyse()`` method of the **Structure** object, the input file sent for analysis via Abaqus in a Python subprocess. The main arguments that ``.analyse()`` takes are: the ``path`` and ``name`` strings associated with the **Structure** object, the ``software`` string set to ``'abaqus'`` to show that we want to use Abaqus, the ``fields`` to extract as a string separated by commas e.g ``'U,S,SM'`` (see Fields and components section later), and the integer number of CPU cores to use ``cpus``. This call could look like for example:

.. code-block:: python

    mdl.analyse(path='/home/al/Temp/', name='simple-truss', software='abaqus', fields='U,S', cpus=2)

This will then initiate a subprocess, launching the Abaqus executable (``abaqus cae``) with no graphical user interface (``noGUI`` mode) and running the **odb.py** script for the requested fields and folder/file names. The purpose of this method is to pair the Abaqus executable with the ``.inp`` file and to generate an ``.odb`` file of data, and is equivalent to manually performing the following in a terminal:

.. code-block:: bash

   abaqus cae noGUI=~/compas_fea/fea/abaq/odb.py -- U,S 2 /home/al/Temp/simple-truss/ /home/al/Temp/ simple-truss

An information stream will print a rolling update of the subprocess progress, and show ``COMPLETED`` if the analysis was successful. If there was not a successful analysis, a variety of error messages will appear to try and help the user evaluate what may have gone wrong. If it is not possible to find out what was wrong with the model from the terminal interface messages, the model should be inspected manually within Abaqus by loading the input file and submitting a job with the job monitor open.

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

-----------------------
Processing of .odb file
-----------------------

The data is extracted from the output database ``.odb`` file with the function ``extract_odb_data()``, which is called automatically as part of the ``.analyse()`` method above. In the same folder as the ``.odb`` file, it will generate a set of ``.json`` files of scraped unprocessed data. These files will all be in the folder **/path/name/** and structured as follows:

- **name-nodes.json**: the key and co-ordinates of the nodes before the analysis {"0": [0.5, 0.875, 1.25], "1": [0.5, 0.125, 1.25], ...}.

- **name-elements.json**: the key and connected nodes of all elements, in the format {"0": [0, 1], "1": [0, 2], "2": [3, 0], "3": [1, 3, 4, 6], ...}.

- **name-step-field.json**: there will be a file for all steps and field data requested. See the next section on how this data is organised.

- **name-step-info.json**: additional log of: frame descriptions, analysis and extraction times and miscellaneous additional information.

- **name-results.json**: all **name-step-field.json** files collected into a dictionary containing all data. This is then saved into the original **Structure** object under ``.results``.


===========================
Fields, components and data
===========================

After the analysis, the data are stored in ``.json`` files and the **Structure** object, where they are accessed by the user to read or visualise the results. The organisation of the collected data in **name-results.json** or ``structure.results`` is in nested dictionaries with keys following a pattern of the: ``step`` string, ``field`` string, ``component`` string of that field and the node or element number string (``structure.results[step][field][component][number]``). The ``field`` and ``component`` strings follow the Abaqus notation which are as follows, where suffixes 1, 2 and 3 correspond to the `x`, `y` and `z` axes:

-----------
Node fields
-----------

- ``'RF'``: reaction forces ``'RF1'``, ``'RF2'`` and ``'RF3'``.

- ``'RM'``: reaction moments ``'RM1'``, ``'RM2'`` and ``'RM3'``.

- ``'U'``: displacements ``'U1'``, ``'U2'`` and ``'U3'``.

- ``'UR'``: rotations ``'UR1'``, ``'UR2'`` and ``'UR3'``.

- ``'CF'``: concentrated forces ``'CF1'``, ``'CF2'`` and ``'CF3'``.

- ``'CM'``: concentrated moments ``'CM1'``, ``'CM2'`` and ``'CM3'``.

- ``'NT'``: nodal temperatures.

- Where applicable, ``'magnitude'`` can be accessed as the component key for the resultant of vector components.

--------------
Element fields
--------------

- ``'SF'`` (beams): section forces ``'SF1'`` axial force, ``'SF2'`` shear force in local y and ``'SF3'`` shear force in local x.

- ``'SF'`` (shells): section forces ``'SF1'`` axial force / width in `x`, ``'SF2'`` axial force / width in `y`, ``'SF3'`` shear force / width, ``'SF4'`` transverse shear force / width in `x` and ``'SF5'`` transverse shear force / width in `y`.

- ``'SM'`` (beams): section moments ``'SM1'`` bending moment about `x`, ``'SM2'`` bending moment about `y` and ``'SM3'`` torsion moment.

- ``'SM'`` (shells): section moments ``'SM1'`` bending moment / width about `y`, ``'SM2'`` bending moment / width about `x` and ``'SM3'`` torsion moment / width.

- ``'SE'`` (beams): section strains ``'SE1'`` axial strain, ``'SE2'`` shear strain in `y` and ``'SE3'`` shear strain in `x`.

- ``'SE'`` (shells): section strains ``'SE1'`` axial strain in `x`, ``'SE2'`` axial strain in `y`, ``'SE3'`` shear strain, ``'SE4'`` transverse shear strain in `x`, ``'SE5'`` transverse shear strain in `y`, ``'SE6'`` through thickness strain.

- ``'SK'`` (beams): section curvatures ``'SK1'`` curvature about `x`, ``'SK2'`` curvature about `y` and ``'SK3'`` twist.

- ``'SK'`` (shells): section curvatures ``'SK1'`` curvature about `y`, ``'SK2'`` curvature about `x` and ``'SK3'`` twist.

- ``'S'`` (beams): stress ``'S11'``, ``'S22'``, ``'S33'`` axial stresses and ``'S12'``. ``'S13'`` ... shear stresses.

- ``'E'``: strain **fill**.

- ``'PE'``: plastic strain **fill**.

- ``'RBFOR'``: reinforcement forces.

- For the tensor fields, ``'mises'``, ``'maxPrincipal'`` and ``'minPrincipal'`` component entries can be requested.

- For elements such as shell elements, the local element axes can be accessed through ``'axes'`` as a component entry.

------------------------------
Integration and section points
------------------------------

For node fields, accessing the displacement in `z`, for step ``'step_load'``, and for node 4 would be ``structure.results['step_load']['U']['U3']['4']``, which would be a single value. For element fields, there is no single data value that can represent the entire element, as each element has physical dimensions and requires many data values across its volume. During a finite element analysis, specific points are evaluated across an element and  section related to the element shape function and cross-section shape (Gauss points). Each of these data-points in the results is stored for the element as an integration point--section point string key. This key looks  like ``'ip4_sp1'``, which would be the data for integration point 4 and section point 1.

The data request ``structure.results['step_load']['S']['mises']['4']``, will, for an example shell element, return a dictionary of data with keys as the integration point--section point keys. For a four noded shell element these would be four integration points (the four internal points, unless a reduced integration scheme is used leading to one point) and two section points (top and bottom layers by default). Details of integration and section points for standard Abaqus elements can be found in the Abaqus documentation, with summaries in the Elements and Sections topics.

Data are stored in this format at each point rather than one value per element for a number of reasons:

- Taking a mean value of all points could give meaningless or misleading results, for example, the mean value of normal stresses in a beam under pure bending would be zero, as positive and negative normal stresses would cancel each other out.

- Selecting one representative integration point is not possible without some understanding of the structural model and loading. For instance, any given point of a beam section will have completely different stress values depending on the degree of major axis or minor axis bending.

- Picking a maximum value of Von Mises stress could be used to find a critical heavily stressed point, as these stresses are always positive. But picking a maximum or minimum value for a stress where the sign matters, as with  compression or tension, is not so straightforward.

