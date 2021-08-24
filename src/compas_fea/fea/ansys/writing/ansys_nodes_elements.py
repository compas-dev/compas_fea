import os

from compas.geometry import add_vectors
from compas.geometry import normalize_vector


# Author(s): Tomas Mendez Echenagucia (github.com/tmsmendez)


def write_elements(structure, output_path, filename):
    structure.et_dict = {}

    # combine elementa and virtual elements ------------------------------------
    elements = {}
    elements.update(structure.elements)
    elements.update(structure.virtual_elements)

    # group sorted elements by type and properties -----------------------------
    ekeys = sorted(elements.keys(), key=int)
    et = elements[ekeys[0]].__name__
    ep = elements[ekeys[0]].element_property
    count = 0
    ekey_lists = [[]]
    for ekey in ekeys:
        if elements[ekey].__name__ == et and elements[ekey].element_property == ep:
            ekey_lists[count].append(ekey)
        else:
            et = elements[ekey].__name__
            ep = elements[ekey].element_property
            ekey_lists.append([ekey])
            count += 1

    # write sorted elements ----------------------------------------------------
    for ekeys in ekey_lists:
        etype = elements[ekeys[0]].__name__
        ep = elements[ekeys[0]].element_property

        if ep:
            ep = structure.element_properties[elements[ekeys[0]].element_property]
        if ep:
            section = ep.section
            material = ep.material

        if etype == 'ShellElement':
            write_shell4_elements(structure, output_path, filename, ekeys, section, material)
        if etype == 'BeamElement':
            write_beam_elements(structure, output_path, filename, ekeys, section, material)
        if etype == 'TieElement' or etype == 'StrutElement' or etype == 'TrussElement':
            write_tie_elements(structure, output_path, filename, ekeys, section, material, etype)
        if etype == 'SpringElement':
            write_spring_elements_nodal(structure, output_path, filename, ekeys, section)
        if etype == 'FaceElement':
            write_surface_elements(structure, output_path, filename, ekeys)
        if etype == 'SolidElement':
            write_solid_elements(structure, output_path, filename, ekeys, material)


def write_virtual_elements(structure, output_path, filename):
    # TODO: DELETE THIS FUNCTION???
    # TODO: this function only works for surface elements, they are they only virtual elements at the moment.
    ekeys = structure.sets['virtual_elements']['selection']
    etypes = {'ShellElement': [], 'BeamElement': [], 'TieElement': [], 'StrutElement': [],
              'TrussElement': [], 'FaceElement': []}
    func_dict = {'ShellElement': write_shell4_elements,
                 'BeamElement': write_beam_elements,
                 'TieElement': write_tie_elements,
                 'StrutElement': write_tie_elements,
                 'TrussElement': write_tie_elements,
                 'SpringElement': write_spring_elements_nodal,
                 'FaceElement': write_surface_elements}

    for ekey in ekeys:
        etypes[structure.virtual_elements[ekey].__name__].append(ekey)

    for etype in etypes:
        ekeys = etypes[etype]
        if ekeys:
            func_dict[etype](structure, output_path, filename, ekeys, None, None)


def write_nodes(structure, output_path, filename):
    cFile = open(os.path.join(output_path, filename), 'a')
    nodes = structure.nodes
    for i in range(len(nodes)):
        node = nodes[i]
        string = 'N,' + str(i + 1) + ',' + str(node.x) + ',' + str(node.y) + ',' + str(node.z) + ',0,0,0 \n'
        cFile.write(string)
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_set_element_material(output_path, filename, mat_index, elem_type, elem_type_index):
    cFile = open(os.path.join(output_path, filename), 'a')
    cFile.write('ET,' + str(elem_type_index) + ',' + str(elem_type) + ' \n')
    cFile.write('TYPE,' + str(elem_type_index) + '\n')
    if elem_type == 'BEAM188':
        cFile.write('KEYOPT, {0},  7, 2 \n'.format(str(elem_type_index)))
        cFile.write('KEYOPT, {0},  9, 3 \n'.format(str(elem_type_index)))
        # cFile.write('KEYOPT, {0}, 15, 1 \n'.format(str(elem_type_index)))
    if mat_index:
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
    etkey = structure.et_dict.setdefault('SHELL181', len(structure.et_dict) + 1)
    write_set_element_material(output_path, filename, mat_index, 'SHELL181', etkey)

    thickness = structure.sections[section].geometry['t']
    write_shell_thickness(output_path, filename, thickness, sec_index, mat_index)

    cFile = open(os.path.join(output_path, filename), 'a')
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


def write_solid_elements(structure, output_path, filename, ekeys, material):
    ekeys = sorted(ekeys, key=int)
    mat_index = structure.materials[material].index
    etkey = structure.et_dict.setdefault('SOLID185', len(structure.et_dict) + 1)
    write_set_element_material(output_path, filename, mat_index, 'SOLID185', etkey)

    cFile = open(os.path.join(output_path, filename), 'a')
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


def write_set_srf_realconstant(output_path, filename, rkey):
    cFile = open(os.path.join(output_path, filename), 'a')
    cFile.write('R,' + str(rkey) + ', , , , , , , , , ,\n')
    cFile.write('REAL,' + str(rkey) + '\n')
    cFile.write('!\n')
    cFile.close()


def write_surface_elements(structure, output_path, filename, ekeys):
    """ This function creates ANSYS shell 181 elements
    in a given ansys input file. These shell elements require 4 nodes.
    """
    ekeys = sorted(ekeys, key=int)
    etkey = structure.et_dict.setdefault('SURF154', len(structure.et_dict) + 1)
    write_set_element_material(output_path, filename, None, 'SURF154', etkey)
    write_set_srf_realconstant(output_path, filename, etkey)

    cFile = open(os.path.join(output_path, filename), 'a')
    for ekey in ekeys:
        element = structure.virtual_elements[ekey].nodes
        string = 'E,'
        if len(element) == 3:
            element.append(element[-1])
        for i in range(len(element)):
            string += str(int(element[i]) + 1)
            if i < len(element) - 1:
                string += ','
        string += '\n'
        cFile.write(string)

    cFile.write('!\n')
    cFile.close()


def write_shell_thickness(output_path, filename, thickness, sec_index, mat_index):
    cFile = open(os.path.join(output_path, filename), 'a')
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

    etkey = structure.et_dict.setdefault('BEAM188', len(structure.et_dict) + 1)
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
    elif sec_type == 'TrapezoidalSection':
        b1 = structure.sections[section].geometry['b1']
        b2 = structure.sections[section].geometry['b2']
        h = structure.sections[section].geometry['h']
        write_trapezoidal_section(output_path, filename, b1, b2, h, sec_index)
    else:
        raise ValueError(sec_type + ' Type of section is not yet implemented for Ansys')

    cFile = open(os.path.join(output_path, filename), 'a')

    for ekey in ekeys:
        element = list(structure.elements[ekey].nodes)
        # print structure.elements[ekey]
        axis = structure.elements[ekey].axes['ex']
        if not axis:
            enode = structure.nodes[element[-1]]
            axis = [0, 1, 0]
        axis = normalize_vector(axis)
        enode = structure.nodes[element[-1]]
        onode = add_vectors([enode.x, enode.y, enode.z], axis)
        nkey = structure.add_node(onode, virtual=True)
        string = 'N,' + str(nkey + 1) + ',' + str(onode[0]) + ',' + str(onode[1])
        string += ',' + str(onode[2]) + ',0,0,0 \n'
        cFile.write(string)

        element.append(nkey)
        string = 'E, '
        for i in range(len(element)):
            string += str(int(element[i]) + 1)
            if i < len(element) - 1:
                string += ','
        string += '\n'
        cFile.write(string)

    cFile.write('!\n')
    cFile.close()


def write_trapezoidal_section(output_path, filename, b1, b2, h, sec_index):
    x1 = b1 / 2.
    x2 = b2 / 2.
    h = h / 2.

    cFile = open(os.path.join(output_path, filename), 'a')
    cFile.write('SECTYPE, ' + str(sec_index + 1) + ', BEAM, QUAD, , 0 \n')
    cFile.write('SECOFFSET, CENT \n')
    cFile.write('SECDATA, -{0}, -{1}, {0}, -{1}, {2}, {1}, -{2}, {1} \n'.format(x1, h, x2))
    cFile.write('SECNUM, ' + str(sec_index + 1) + '\n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_i_section(output_path, filename, height, base, thickness_w, thickness_f, sec_index):
    cFile = open(os.path.join(output_path, filename), 'a')
    cFile.write('SECTYPE, ' + str(sec_index + 1) + ', BEAM, I, , 0 \n')
    cFile.write('SECOFFSET, CENT \n')
    cFile.write('SECDATA,' + str(base) + ',' + str(base) + ',' + str(height) + ',')
    cFile.write(str(thickness_f) + ',' + str(thickness_f) + ',' + str(thickness_w) + '\n')
    cFile.write('SECNUM, ' + str(sec_index) + ' \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_angle_section(output_path, filename, height, base, thickness, sec_index):
    cFile = open(os.path.join(output_path, filename), 'a')
    cFile.write('SECTYPE, ' + str(sec_index + 1) + ', BEAM, L, , 0 \n')
    cFile.write('SECOFFSET, CENT \n')
    cFile.write('SECDATA,' + str(base) + ',' + str(height) + ',' + str(thickness) + ',' + str(thickness) + '\n')
    cFile.write('SECNUM, ' + str(sec_index + 1) + ' \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_rectangular_beam_section(output_path, filename, height, base, sec_index):
    cFile = open(os.path.join(output_path, filename), 'a')
    cFile.write('SECTYPE, ' + str(sec_index + 1) + ', BEAM, RECT, , 0 \n')
    cFile.write('SECOFFSET, CENT \n')
    cFile.write('SECDATA,' + str(height) + ',' + str(base) + '\n')
    cFile.write('SECNUM, ' + str(sec_index + 1) + ' \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_pipe_section(output_path, filename, in_radius, thickness, sec_index):
    cFile = open(os.path.join(output_path, filename), 'a')
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

    etkey = structure.et_dict.setdefault('LINK180', len(structure.et_dict) + 1)
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

    cFile = open(os.path.join(output_path, filename), 'a')
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
    cFile = open(os.path.join(output_path, filename), 'a')
    cFile.write('R,' + str(sec_index + 1) + ',' + str(sec_area) + ', ,1  \n')
    cFile.write('REAL,' + str(sec_index + 1) + '\n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_circular_section(output_path, filename, radius, sec_index):
    cFile = open(os.path.join(output_path, filename), 'a')
    cFile.write('SECTYPE, ' + str(sec_index + 1) + ', BEAM, CSOLID , 0 \n')
    cFile.write('SECOFFSET, CENT \n')
    cFile.write('SECDATA,' + str(radius) + ',8\n')
    cFile.write('SECNUM, ' + str(sec_index + 1) + '\n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_request_element_nodes(path, name):
    out_path = os.path.join(path, name + '_output')

    filename = name + '_extract.txt'

    cFile = open(os.path.join(path, filename), 'a')
    cFile.write('/POST1 \n')
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.write('SET, FIRST \n')

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


def write_request_node_displacements(structure, step_index, mode=None):
    name = structure.name
    path = structure.path
    step_name = structure.steps_order[step_index]

    out_path = os.path.join(path, name + '_output')
    filename = name + '_extract.txt'
    if mode:
        fname = 'modal_shape_' + str(mode)
        name_ = 'nds_d' + str(mode)
        name_x = 'dispX' + str(mode)
        name_y = 'dispY' + str(mode)
        name_z = 'dispZ' + str(mode)
        out_path = os.path.join(out_path, 'modal_out')
    else:
        fname = str(step_name) + '_' + 'displacements'
        name_ = 'nds_d'
        name_x = 'dispX'
        name_y = 'dispY'
        name_z = 'dispZ'

    cFile = open(os.path.join(path, filename), 'a')
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

    # fh = open(os.path.join(path, filename), 'a')
    # fh.write('*get, nnodes, node,, count \n')
    # fh.write('*dim, u, array, nnodes, 5 \n')
    # fh.write('! \n')

    # fh.write('*do, i, 1, nnodes \n')
    # fh.write('u(i,1) = i                         !Collumn 1 is node number \n')
    # fh.write('*get, u(i,2), NODE, u(i,1), U, X   !Collumn 2 is Ux \n')
    # fh.write('*get, u(i,3), NODE, u(i,1), U, Y   !Collumn 3 is Uy \n')
    # fh.write('*get, u(i,4), NODE, u(i,1), U, Z   !Collumn 4 is Uz \n')
    # fh.write('*get, u(i,5), NODE, u(i,1), U, SUM !Collumn 5 is Um \n')
    # fh.write('*Enddo \n')
    # fh.write('! \n')

    # fh.write('*cfopen,' + out_path + '/' + fname + ',txt \n')
    # fh.write('*CFWRITE, node U, num, ux, uy, uz, uSUM \n')
    # fh.write('*do,i,1,nnodes \n')
    # fh.write('*CFWRITE, node U, u(i,1), u(i,2), u(i,3), u(i,4), u(i,5) \n')
    # fh.write('*Enddo \n')
    # fh.close()


def write_constraint_nodes(structure, output_path, filename, displacements):
    cFile = open(os.path.join(output_path, filename), 'a')

    cdict = {'x': 'UX', 'y': 'UY', 'z': 'UZ', 'xx': 'ROTX', 'yy': 'ROTY', 'zz': 'ROTZ'}

    if type(displacements) != list:
        displacements = [displacements]

    for dkey in displacements:
        components = structure.displacements[dkey].components
        nodes = structure.displacements[dkey].nodes
        if type(nodes) == str:
            nodes = structure.sets[nodes].selection
        for node in nodes:
            for com in components:
                if components[com] is not None:
                    string = 'D, {0}, {1}, {2} \n'.format(str(node + 1), cdict[com], components[com])
                    cFile.write(string)

    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_areas(structure, output_path, filename):
    areas = structure.areas
    areas_keys = sorted(areas.keys(), key=int)

    cFile = open(os.path.join(output_path, filename), 'a')

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
    cFile = open(os.path.join(output_path, filename), 'a')
    nodes = structure.nodes
    for i in range(len(nodes)):
        node = nodes[i]
        string = 'K,' + str(i + 1) + ',' + str(node['x']) + ',' + str(node['y']) + ',' + str(node['z']) + '\n'
        cFile.write(string)
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.close()


def write_volume_areas(output_path, filename):
    cFile = open(os.path.join(output_path, filename), 'a')
    string = 'VA,ALL \n'
    cFile.write(string)
    cFile.write('!\n')
    cFile.close()


def write_request_mesh_areas(structure, output_path, name, size=None, smart_size=None, div=None):
    filename = name + '.txt'

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    write_nodes_as_keypoints(structure, output_path, filename)
    write_areas(structure, output_path, filename)

    # This function uses ansys meshing algorithm to mesh all areas present in the model
    # and writes "nodes.txt" with the new nodes and "elements.txt" with the resulting elements.

    cFile = open(os.path.join(output_path, filename), 'a')
    cFile.write('ET,1,SHELL181 \n')
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

    out_path = os.path.join(output_path, name + '_output')

    cFile.write('/POST1 \n')
    cFile.write('!\n')
    cFile.write('!\n')
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


def write_request_mesh_volume(structure, output_path, name, size=1, hex=True, div=None):
    filename = name + '.txt'

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    write_nodes_as_keypoints(structure, output_path, filename)
    write_areas(structure, output_path, filename)
    write_volume_areas(output_path, filename)

    # This function uses ansys meshing algorithm to mesh all volumes present
    # in the model and writes "nodes.txt" with the new nodes and "elements.txt"
    # with the resulting elements.

    if hex:
        shape = 0
        et = 'SOLID185'
        size_str = 'ESIZE,0,{0} \n'.format(div)
    else:
        shape = 1
        et = 'SOLID185'
        size_str = 'SMRTSIZE, {0} \n'.format(size)

    cFile = open(os.path.join(output_path, filename), 'a')
    cFile.write('ET, 1, {0} \n'.format(et))  # shold the element type key be taken from somewhere?
    cFile.write('!\n')
    cFile.write('!\n')
    cFile.write('MSHAPE, {0}, 3D \n'.format(shape))
    cFile.write(size_str)
    # cFile.write('SMRTSIZE,,2,2,2,40,40,2,OFF,OFF,4,OFF \n')
    cFile.write('VMESH, all,, \n')
    cFile.write('!\n')
    cFile.write('!\n')

    out_path = os.path.join(output_path, name + '_output')

    cFile.write('/POST1 \n')
    cFile.write('!\n')
    cFile.write('!\n')
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


def write_spring_elements_nodal(structure, out_path, filename, ekeys, section):
    axis_dict = {'x': 1, 'y': 2, 'z': 3, 'xx': 4, 'yy': 5, 'zz': 6}
    kdict = section.stiffness
    fh = open(os.path.join(out_path, filename), 'a')
    for axis in kdict:
        etkey = structure.et_dict.setdefault('COMBIN14_' + axis, len(structure.et_dict) + 1)
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
