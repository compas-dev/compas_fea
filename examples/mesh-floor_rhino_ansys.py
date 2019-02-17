# .obj filename
fnm = 'C:/Users/mtomas/Desktop/stuff_mesh/build_mesh_load.obj'

# Generate Ansys input file
outpath = 'C:/Users/mtomas/Desktop/stuff_mesh/'
fnl = 'build_mesh_load.txt'
ansys.inp_generate(structure=mdl, output_path =outpath, filename=fnl)

# Run in Ansys in the background -----------------------------------------------
# Submit job for analysis
ansys_path = 'C:/Program Files/ANSYS Inc/v145/ANSYS/bin/winx64/ansys145.exe'
ansys.launch_process(structure=mdl,output_path=outpath,filename=fnl,ansys_path=ansys_path)
