import os

__author__     = ['Tomas Mendez Echenagucia <mendez@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'mendez@arch.ethz.ch'


et_dict = {}


def write_elements(structure, output_path, filename):
    ep = structure.element_properties
    for key in ep:
        section = ep[key].section
        material = ep[key].material
        elsets = ep[key].elsets
        ekeys = []
        if elsets:
            for elset in elsets:
                if elset == 'ELSET_ALL':
                    ekeys.extend(structure.elements)
                else:
                    ekeys.extend(structure.sets[elset]['selection'])
        if ep[key].elements:
            ekeys.extend(ep[key].elements)
        etype = structure.elements[ekeys[0]].__name__
        if etype == 'ShellElement':
            write_shell4_elements(structure, output_path, filename, ekeys, section, material)
        if etype == 'BeamElement':
            write_beam_elements(structure, output_path, filename, ekeys, section, material)
        if etype == 'TieElement' or etype == 'StrutElement' or etype == 'TrussElement':
            write_tie_elements(structure, output_path, filename, ekeys, section, material, etype)
        if etype == 'SpringElement':
            write_spring_elements_nodal(structure, output_path, filename, ekeys, section)


def write_nodes(structure, output_path, filename):
    cFile = open(output_path + '/' + filename, 'a')
    nodes = structure.nodes
    for i in range(len(nodes)):
        node = nodes[i]
        string = 'N,' + str(i + 1) + ',' + str(node['x']) + ',' + str(node['y']) + ',' + str(node['z']) + ',0,0,0 \n'
        cFile.write(string)
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_set_element_material(output_path, filename, mat_index, elem_type, elem_type_index):
    cFile = open(output_path + "/" + filename, 'a')
    cFile.write('ET,' + str(elem_type_index) + ',' + str(elem_type) + ' \n')
    cFile.write('TYPE,' + str(elem_type_index) + '\n')
    cFile.write('MAT,' + str(mat_index + 1) + '\n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_shell4_elements(structure, output_path, filename, ekeys, section, material):
    """ This function creates ANSYS shell 181 elements
    in a given ansys input file. These shell elements require 4 nodes.
    """
    ekeys = sorted(ekeys, key=int)
    mat_index = structure.materials[material].index
    sec_index = structure.sections[section].index
    etkey = et_dict.setdefault('SHELL181', len(et_dict) + 1)
    write_set_element_material(output_path, filename, mat_index, 'SHELL181', etkey)

    thickness = structure.sections[section].geometry['t']
    write_shell_thickness(output_path, filename, thickness, sec_index, mat_index)

    cFile = open(output_path + "/" + filename, 'a')
    for ekey in ekeys:
        element = structure.elements[ekey]
        element = element.nodes
        string = 'E,'
        for i in range(len(element)):
            string += str(int(element[i]) + 1)
            if i < len(element) - 1:
                string += ','
        string += '\n'
        cFile.write(string)

    cFile.write('!\n')
    cFile.close()


def write_shell_thickness(output_path, filename, thickness, sec_index, mat_index):
    cFile = open(output_path + "/" + filename, 'a')
    cFile.write('SECTYPE,' + str(sec_index + 1) + ',SHELL,, \n')
    cFile.write('SECDATA, ' + str(thickness) + ',' + str(mat_index) + ',0.0,3\n')
    cFile.write('SECOFFSET,MID\n')
    cFile.write('SECNUM,' + str(sec_index + 1) + '\n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_beam_elements(structure, output_path, filename, ekeys, section, material):

    ekeys = sorted(ekeys, key=int)
    mat_index = structure.materials[material].index
    sec_index = structure.sections[section].index

    etkey = et_dict.setdefault('BEAM188', len(et_dict) + 1)
    write_set_element_material(output_path, filename, mat_index, 'BEAM188', etkey)
    sec_type = structure.sections[section].__name__
    if sec_type == 'PipeSection':
        thickness = structure.sections[section].geometry['t']
        in_radius = structure.sections[section].geometry['r']
        write_pipe_section(output_path, filename, in_radius, thickness, sec_index)
    elif sec_type == 'RectangularSection':
        height = structure.sections[section].geometry['h']
        base = structure.sections[section].geometry['b']
        write_rectangular_beam_section(output_path, filename, height, base, sec_index)
    elif sec_type == 'CircularSection':
        radius = structure.sections[section].geometry['r']
        write_circular_section(output_path, filename, radius, sec_index)
    elif sec_type == 'AngleSection':
        base = structure.sections[section].geometry['b']
        height = structure.sections[section].geometry['h']
        thickness = structure.sections[section].geometry['t']
        write_angle_section(output_path, filename, height, base, thickness, sec_index)
    elif sec_type == 'ISection':
        base = structure.sections[section].geometry['b']
        height = structure.sections[section].geometry['h']
        thickness_w = structure.sections[section].geometry['tf']
        thickness_f = structure.sections[section].geometry['tw']
        write_i_section(output_path, filename, height, base, thickness_w, thickness_f, sec_index)

    orient = structure.sections[section].orientation

    cFile = open(output_path + "/" + filename, 'a')
    for ekey in ekeys:
        element = structure.elements[ekey].nodes
        if orient:
            enode = structure.nodes[element[-1]]
            onode = [enode['x'] + orient[0], enode['y'] + orient[1], enode['z'] + orient[2]]
            string = 'N,' + str(structure.node_count()) + ',' + str(onode[0]) + ',' + str(onode[1])
            string += ',' + str(onode[2]) + ',0,0,0 \n'
            cFile.write(string)
            element.append(structure.node_count() - 1)
        string = 'E,'
        for i in range(len(element)):
            string += str(int(element[i]) + 1)
            if i < len(element) - 1:
                string += ','
        string += '\n'
        cFile.write(string)

    cFile.write('!\n')
    cFile.close()


def write_i_section(output_path, filename, height, base, thickness_w, thickness_f, sec_index):
    cFile = open(output_path + "/" + filename, 'a')
    cFile.write('SECTYPE, ' + str(sec_index + 1) + ', BEAM, I, , 0 \n')
    cFile.write('SECOFFSET, CENT \n')
    cFile.write('SECDATA,' + str(base) + ',' + str(base) + ',' + str(height) + ',')
    cFile.write(str(thickness_f) + ',' + str(thickness_f) + ',' + str(thickness_w) + '\n')
    cFile.write('SECNUM, ' + str(sec_index) + ' \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_angle_section(output_path, filename, height, base, thickness, sec_index):
    cFile = open(output_path + "/" + filename, 'a')
    cFile.write('SECTYPE, ' + str(sec_index + 1) + ', BEAM, L, , 0 \n')
    cFile.write('SECOFFSET, CENT \n')
    cFile.write('SECDATA,' + str(base) + ',' + str(height) + ',' + str(thickness) + ',' + str(thickness) + '\n')
    cFile.write('SECNUM, ' + str(sec_index + 1) + ' \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_rectangular_beam_section(output_path, filename, height, base, sec_index):
    cFile = open(output_path + "/" + filename, 'a')
    cFile.write('SECTYPE, ' + str(sec_index + 1) + ', BEAM, RECT, , 0 \n')
    cFile.write('SECOFFSET, CENT \n')
    cFile.write('SECDATA,' + str(height) + ',' + str(base) + '\n')
    cFile.write('SECNUM, ' + str(sec_index + 1) + ' \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_pipe_section(output_path, filename, in_radius, thickness, sec_index):
    cFile = open(output_path + "/" + filename, 'a')
    cFile.write('SECTYPE, ' + str(sec_index + 1) + ', BEAM, CTUBE, , 0 \n')
    cFile.write('SECOFFSET, CENT \n')
    cFile.write('SECDATA,' + str(in_radius) + ',' + str(in_radius + thickness) + ',8\n')
    cFile.write('SECNUM, ' + str(sec_index + 1) + '\n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_tie_elements(structure, output_path, filename, ekeys, section, material, etype):

    ekeys = sorted(ekeys, key=int)
    mat_index = structure.materials[material].index
    sec_index = structure.sections[section].index

    etkey = et_dict.setdefault('LINK180', len(et_dict) + 1)
    write_set_element_material(output_path, filename, mat_index, 'LINK180', etkey)

    # axial_force =  0 for tension and compression, 1 tension only, 2 compression only
    if etype == 'TieElement':
        sec_area = structure.sections[section].geometry['A']
        write_tie_section(output_path, filename, sec_area, sec_index, axial_force=2)
    elif etype == 'StrutElement':
        sec_area = structure.sections[section].geometry['A']
        write_tie_section(output_path, filename, sec_area, sec_index, axial_force=1)
    elif etype == 'TrussElement':
        sec_area = structure.sections[section].geometry['A']
        write_tie_section(output_path, filename, sec_area, sec_index, axial_force=0)

    cFile = open(output_path + "/" + filename, 'a')
    for ekey in ekeys:
        element = structure.elements[ekey].nodes
        string = 'E,'
        for i in range(len(element)):
            string += str(int(element[i]) + 1)
            if i < len(element) - 1:
                string += ','
        string += '\n'
        cFile.write(string)

    cFile.write('!\n')
    cFile.close()


def write_tie_section(output_path, filename, sec_area, sec_index, axial_force):
    cFile = open(output_path + "/" + filename, 'a')
    cFile.write('R,' + str(sec_index + 1) + ',' + str(sec_area) + ', ,1  \n')
    cFile.write('REAL,' + str(sec_index + 1) + '\n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_circular_section(output_path, filename, radius, sec_index):
    cFile = open(output_path + "/" + filename, 'a')
    cFile.write('SECTYPE, ' + str(sec_index + 1) + ', BEAM, CSOLID , 0 \n')
    cFile.write('SECOFFSET, CENT \n')
    cFile.write('SECDATA,' + str(radius) + ',8\n')
    cFile.write('SECNUM, ' + str(sec_index + 1) + '\n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_request_element_nodes(path, name):
    out_path = path + '/' + name + '_output/'
    filename = name + '_extract.txt'

    cFile = open(path + filename, 'a')
    cFile.write('/POST1 \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.write('SET,FIRST \n')

    cFile.write('!\n')
    cFile.write('*get,num_nodes,node,,count \n')
    cFile.write('*set,nodeX, \n')
    cFile.write('*dim,nodeX,array,num_nodes,1 \n')
    cFile.write('*set,nodeY, \n')
    cFile.write('*dim,nodeY,array,num_nodes,1 \n')
    cFile.write('*set,nodeZ, \n')
    cFile.write('*dim,nodeZ,array,num_nodes,1 \n')
    cFile.write('*dim,nds, ,num_nodes \n')
    cFile.write('*VGET, nodeX, node, all, loc, X,,,2 \n')
    cFile.write('*VGET, nodeY, node, all, loc, Y,,,2 \n')
    cFile.write('*VGET, nodeZ, node, all, loc, Z,,,2 \n')
    cFile.write('*vfill,nds(1),ramp,1,1 \n')
    cFile.write('*cfopen,' + out_path + '/nodes,txt \n')
    cFile.write('*vwrite, nds(1) , \',\'  , nodeX(1) ,   \',\' ,   nodeY(1) ,   \',\' ,  nodeZ(1) \n')
    cFile.write('(F8.0, A, ES, A, ES, A, ES) \n')
    cFile.write('*cfclose \n')
    cFile.write('!\n')
    cFile.write('!\n')

    cFile.write('*get,numElem,elem,,count \n')
    cFile.write('*set,elem1, \n')
    cFile.write('*dim,elem1,array,numElem,1 \n')
    cFile.write('*set,elem2, \n')
    cFile.write('*dim,elem2,array,numElem,1 \n')
    cFile.write('*set,elem3, \n')
    cFile.write('*dim,elem3,array,numElem,1 \n')
    cFile.write('*set,elem4, \n')
    cFile.write('*dim,elem4,array,numElem,1 \n')
    cFile.write('*set,elem5, \n')
    cFile.write('*dim,elem5,array,numElem,1 \n')
    cFile.write('*set,elem6, \n')
    cFile.write('*dim,elem6,array,numElem,1 \n')
    cFile.write('*set,elem7, \n')
    cFile.write('*dim,elem7,array,numElem,1 \n')
    cFile.write('*set,elem8, \n')
    cFile.write('*dim,elem8,array,numElem,1 \n')
    cFile.write('*set,elemType, \n')
    cFile.write('*dim,elemType,array,numElem,1 \n')
    cFile.write('*set,elemMat, \n')
    cFile.write('*dim,elemMat,array,numElem,1 \n')
    cFile.write('*set,elemSec, \n')
    cFile.write('*dim,elemSec,array,numElem,1 \n')

    cFile.write('*VGET, elem1, elem, all, node, 1,,,2 \n')
    cFile.write('*VGET, elem2, elem, all, node, 2,,,2 \n')
    cFile.write('*VGET, elem3, elem, all, node, 3,,,2 \n')
    cFile.write('*VGET, elem4, elem, all, node, 4,,,2 \n')
    cFile.write('*VGET, elem5, elem, all, node, 5,,,2 \n')
    cFile.write('*VGET, elem6, elem, all, node, 6,,,2 \n')
    cFile.write('*VGET, elem7, elem, all, node, 7,,,2 \n')
    cFile.write('*VGET, elem8, elem, all, node, 8,,,2 \n')
    cFile.write('*VGET, elemType, elem, all,attr,TYPE,,,2 \n')
    cFile.write('*VGET, elemMat, elem, all,attr,mat,,,2 \n')
    cFile.write('*VGET, elemSec, elem, all,attr,secn,,,2 \n')

    cFile.write('*cfopen,' + out_path + '/elements,txt \n')
    cFile.write('*vwrite,  elem1(1),elem2(1),elem3(1),elem4(1),elem5(1),elem6(1)')
    cFile.write(',elem7(1),elem8(1), \',\',elemType(1),elemMat(1),elemSec(1) \n')
    cFile.write('(F9.0,TL1,' ',F9.0,TL1,' ',F9.0,TL1,' ',F9.0,TL1,' ',F9.0,TL1,' ',')
    cFile.write('F9.0,TL1,' ',F9.0,TL1,' ',F9.0,TL1,' ',A,F9.0,TL1,' ',F9.0,TL1,' ',F9.0,TL1,' ') \n')

    cFile.write('*cfclose \n')
    cFile.write('!\n')
    cFile.write('!\n')

    cFile.close()


def write_request_node_displacements(path, name, step_name, mode=None):
    out_path = path + '/' + name + '_output/'
    filename = name + '_extract.txt'
    if mode:
        fname = 'modal_shape_' + str(mode)
        name_ = 'nds_d' + str(mode)
        name_x = 'dispX' + str(mode)
        name_y = 'dispY' + str(mode)
        name_z = 'dispZ' + str(mode)
        out_path += 'modal_out/'
    else:
        fname = str(step_name) + '_' + 'displacements'
        name_ = 'nds_d'
        name_x = 'dispX'
        name_y = 'dispY'
        name_z = 'dispZ'

    cFile = open(path + filename, 'a')
    cFile.write('/POST1 \n')
    cFile.write('!\n')
    cFile.write('*get,numNodes,node,,count \n')
    cFile.write('*set,' + name_x + ', \n')
    cFile.write('*dim,' + name_x + ',array,numNodes,1 \n')
    cFile.write('*set,' + name_y + ', \n')
    cFile.write('*dim,' + name_y + ',array,numNodes,1 \n')
    cFile.write('*set,' + name_z + ', \n')
    cFile.write('*dim,' + name_z + ',array,numNodes,1 \n')
    cFile.write('*dim,' + name_ + ', ,numNodes \n')
    cFile.write('*VGET, ' + name_x + ', node, all, u, X,,,2 \n')
    cFile.write('*VGET, ' + name_y + ', node, all, u, Y,,,2 \n')
    cFile.write('*VGET, ' + name_z + ', node, all, u, Z,,,2 \n')
    cFile.write('*vfill,' + name_ + '(1),ramp,1,1 \n')
    cFile.write('*cfopen,' + out_path + '/' + fname + ',txt \n')
    cFile.write('*vwrite, ' + name_ + '(1) , \',\'  , ' + name_x + '(1) , \',\' , ')
    cFile.write(name_y + '(1) , \',\' ,' + name_z + '(1) \n')
    cFile.write('(          F9.0,       A,       ES,           A,          ES,          A,      ES) \n')
    cFile.write('*cfclose \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_constraint_nodes(structure, output_path, filename, displacements):
    cFile = open(output_path + "/" + filename, 'a')

    for dkey in displacements:
        components = structure.displacements[dkey].components
        string = ''
        if components['x'] == 0:
            string += 'UX,'
        else:
            string += ' ,'
        if components['y'] == 0:
            string += 'UY,'
        else:
            string += ' ,'
        if components['z'] == 0:
            string += 'UZ,'
        else:
            string += ' ,'
        if components['xx'] == 0:
            string += 'ROTX,'
        else:
            string += ' ,'
        if components['yy'] == 0:
            string += 'ROTY,'
        else:
            string += ' ,'
        if components['zz'] == 0:
            string += 'ROTZ,'
        else:
            string += '  '

        nodes = structure.displacements[dkey].nodes
        if type(nodes) == str:
            nodes = structure.sets[nodes]['selection']
        for node in nodes:
            string_ = 'D,' + str(int(node) + 1) + ', ,0, , , ,' + string + ' \n'
            cFile.write(string_)

    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_areas(structure, output_path, filename):

    areas = structure.areas
    areas_keys = sorted(areas.keys(), key=int)

    cFile = open(output_path + "/" + filename, 'a')

    for akey in areas_keys:
        area = areas[akey]
        string = 'A,'
        for i in range(len(area)):
            string += str(int(area[i]) + 1)
            if i < len(area) - 1:
                string += ','
        string += '\n'
        cFile.write(string)

    cFile.write('!\n')
    cFile.close()


def write_nodes_as_keypoints(structure, output_path, filename):
    cFile = open(output_path + "/" + filename, 'a')
    nodes = structure.nodes
    for i in range(len(nodes)):
        node = nodes[i]
        string = 'K,' + str(i + 1) + ',' + str(node['x']) + ',' + str(node['y']) + ',' + str(node['z']) + '\n'
        cFile.write(string)
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_request_mesh_areas(structure, output_path, filename, size=None, smart_size=None, div=None):

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    write_nodes_as_keypoints(structure, output_path, filename)
    write_areas(structure, output_path, filename)

    # This function uses ansys meshing algorithm to mesh all areas present in the model
    # and writes "nodes.txt" with the new nodes and "elements.txt" with the resulting elements.

    cFile = open(output_path + "/" + filename, 'a')
    cFile.write('ET,1,SHELL281 \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.write('MSHAPE,1,2D \n')
    if size:
        cFile.write('ESIZE,' + str(size) + ', \n')
    elif div:
        cFile.write('ESIZE,,' + str(div) + ', \n')
    elif smart_size:
        cFile.write('SMRTSIZE,' + str(smart_size) + ', \n')
    else:
        cFile.write('SMRTSIZE,4, \n')
        # cFile.write('SMRTSIZE,,0.2,0.8,2 \n') # Smart custom 1
    # cFile.write('ESIZE,0.05, \n')
    # cFile.write('ESIZE,,5 \n')
    # cFile.write('SMRTSIZE,4 \n')
    # cFile.write('SMRTSIZE,,0.2,1.5,2 \n')
    cFile.write('AMESH,all,, \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()
    write_request_element_nodes(output_path, filename)


def write_spring_elements_nodal(structure, out_path, filename, ekeys, section):
    axis_dict = {'x': 1, 'y': 2, 'z': 3, 'xx': 4, 'yy': 5, 'zz': 6}
    kdict = section.stiffness
    fh = open(out_path + "/" + filename, 'a')
    for axis in kdict:
        etkey = et_dict.setdefault('COMBIN14_' + axis, len(et_dict) + 1)
        fh.write('ET, {0}, COMBIN14 \n'.format(etkey))
        fh.write('KEYOPT, {0}, 1, 0 \n'.format(etkey))
        fh.write('KEYOPT, {0}, 2, {1} \n'.format(etkey, axis_dict[axis]))
        # fh.write('KEYOPT, {0}, 3, 1 \n'.format(etkey))
        fh.write('R, {0}, {1} \n'.format(etkey, kdict[axis]))
        fh.write('TYPE, {0} \n'.format(etkey))
        fh.write('REAL, {0} \n'.format(etkey))
        fh.write('! \n')
        for ekey in ekeys:
            element = structure.elements[ekey].nodes
            string = 'E, ' + str(int(element[0]) + 1) + ', ' + str(int(element[1]) + 1) + '\n'
            fh.write(string)
        fh.write('! \n')
    fh.write('! \n')
    fh.close()
















