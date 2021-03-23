# COMPAS FEA

![build](https://github.com/compas-dev/compas_fea/workflows/build/badge.svg)
[![GitHub - License](https://img.shields.io/github/license/compas-dev/compas_fea.svg)](https://github.com/compas-dev/compas_fea)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/compas_fea.svg)](https://pypi.python.org/project/compas_fea)
[![PyPI - Latest Release](https://img.shields.io/pypi/v/compas_fea.svg)](https://pypi.python.org/project/compas_fea)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.2553836.svg)](https://doi.org/10.5281/zenodo.2553836)

Finite Element Analysis for COMPAS.

Finite element analysis is a numerical approach to solving a variety of problems in the sciences, mathematics and engineering fields. A continuum such as a fluid or solid volume, is discretised into a set of smaller discrete elements. For each element, data of interest, such as stresses, displacements, temperatures and so on, are found at the nodes and element integration points. The greater the number of elements used to represent the continuum, the better the numerical model will represent the original continuous solution.

The **compas_fea** package of the **compas** framework seeks to aid the user, be they an architect, scientist or engineer, in creating and analysing a suitable finite element model for their problem. This is done by creating a **Structure** object, to contain geometric information about the model, and then to apply loads, displacements, materials and so forth for a subsequent analysis. This construction of the **Structure** object may be performed in a pure scripting manner with Python, and/or through various modules that help construct the object through present or parametrically generated geometry.

Once the model has been constructed, it may be analysed through a finite element solver in the background, with the data then stored back into the original object or as raw data files. The data can then be post-processed to display the results either through standard compas viewers and applications, or with visualisation support from specific CAD or finite element software.

By using the **compas_fea** package, the majority of the repetitive scripting tasks needed to perform a geometrically or structurally complex analysis are eliminated, allowing for the rapid investigation of models, with easy to use and streamlined data post-processing and visualisation support.

## Installation

## First Steps

## Questions and Feedback

## Issue Tracker

## License

## Credits
