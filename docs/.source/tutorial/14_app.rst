********************************************************************************
App
********************************************************************************

This page describes the use of the **compas_fea** App, which can be used for visualising the geometry of the created **Structure** and later (when implemented) for plotting the results from the analysis.


=====================
Viewing the Structure
=====================

The App may be invoked by using the ``structure.view()`` method, which will take the geometry information stored in the ``.nodes`` and ``.elements`` dictionaries, and plot an OpenGL/Vtk based 3D representation of the **Structure**. To load and view a **Structure** from an ``.obj' file, use the following code:

.. code-block:: python

    from compas_fea.structure import Structure

    fnm = '/home/al/mesh_roof.obj'

    mdl = Structure.load_from_obj(fnm)
    mdl.view()

The App, as shown in the figure below, will plot: 1) 1D line elements in blue for beams, red for trusses and yellow for springs, 2) 2D shell elements will be plotted as mesh faces in green, and 3) free nodes will be plotted as points in blue and nodes with some displacement object attached to them plotted in orange.

.. image:: /_images/roof_app.png
   :scale: 45 %
