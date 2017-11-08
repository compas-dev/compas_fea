from compas_fea.fea.ansys import ansys_launch_process
from compas_fea.fea.ansys.writing.ansys_process import ansys_open_post_process

__author__     = ['Tomas Mendez Echenagucia <mendez@arch.ethz.ch>']
__copyright__  = 'Copyright 2017, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'mendez@arch.ethz.ch'


def run_mac(name, path, file1, lstep1, file2, lstep2, num_modes, cpus=2, license='research'):

    write_request_mac_ansys(name, path, file1, lstep1, file2, lstep2, num_modes)
    ansys_launch_process(path, name, None, cpus=cpus, license=license, delete=False)
    mac = read_mac_results_file(name, path)
    return mac


def read_mac_results_file(name, path):
    filename = 'mac.txt'
    out_path = path + '/' + name + '_output/'
    fh = open(out_path + filename, 'r')
    lines = fh.readlines()
    mac = {}
    for i, line in enumerate(lines):
        mode_string = line.split(',')
        mac_list = map(float, mode_string)
        mac[i] = dict((j, m) for (j, m) in enumerate(mac_list))
        mac[i]['best_match'] = mac_list.index(max(mac_list))
        mac[i]['best_mac'] = max(mac_list)
    return mac


def write_request_mac_ansys(name, path, file1, lstep1, file2, lstep2, num_modes):
    filename = name + '.txt'
    out_path = path + '/' + name + '_output/'
    ansys_open_post_process(path, filename)

    cFile = open(path + "/" + filename, 'a')
    cFile.write('RSTMAC,' + file1 + ',' + str(lstep1) + ',all,' + file2 + ',' + str(lstep2) + ',all,,0.01,,1 \n')

    for i in range(num_modes):
        cFile.write('*set,mac' + str(i + 1) + ', \n')
        cFile.write('*dim,mac' + str(i + 1) + ',array,' + str(num_modes) + ', \n')
        for j in range(num_modes):
            cFile.write('*GET, mac' + str(i + 1) + '(' + str(j + 1) + '), RSTMAC,' + str(j + 1) + ', MAC, ' + str(i + 1) + ' \n')
    cFile.write('*cfopen,' + out_path + '/mac,txt \n')
    string = '*vwrite, '
    string_ = '('
    for i in range(num_modes):
        string += 'mac' + str(i + 1) + '(1), \',\', '
        string_ += 'ES, A, '
    string = string.rstrip(', \',\', ')
    string_ = string_.rstrip(', A, ')
    cFile.write(string + ' \n')
    cFile.write(string_ + ') \n')
    cFile.write('*cfclose \n')
    cFile.close()
