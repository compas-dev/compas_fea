from compas_fea.fea.ansys import ansys_launch_process
from compas_fea.fea.ansys.writing.ansys_modal import write_request_mac_ansys


def run_mac(name, path, file1, lstep1, file2, lstep2, num_modes, cpus=2, license='research'):

    write_request_mac_ansys(name, path, file1, lstep1, file2, lstep2, num_modes)
    ansys_launch_process(path, name, None, cpus=cpus, license=license, delete=False)
