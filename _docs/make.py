from importlib import import_module

modules = [
    'compas_fea',
    'compas_fea.cad',
    'compas_fea.fea',
    'compas_fea.structure',
]


for name in modules:
    obj = import_module(name)

    print obj

    with open('source/pages/reference/{0}.rst'.format(name), 'wb+') as fp:
        fp.write(obj.__doc__)
