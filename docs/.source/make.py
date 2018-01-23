from importlib import import_module

import os
import sys

modules = [
    'compas_fea',
    'compas_fea.cad',
    'compas_fea.fea',
    'compas_fea.structure',
    'compas_fea.utilities',
]

for name in modules:
    obj = import_module(name)

    print(obj)
	# havent added relative path yet

    # with open('/Users/mtomas/Documents/compas/packages/compas_fea/docs/.source/reference/{0}.rst'.format(name), 'w+') as fp:
    #     fp.write(obj.__doc__)

    with open('/al/compas_fea/docs/.source/reference/{0}.rst'.format(name), 'w+') as fp:
        fp.write(obj.__doc__)
