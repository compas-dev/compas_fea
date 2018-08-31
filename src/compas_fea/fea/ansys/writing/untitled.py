

freq_list = range(10,200,10)
sind = 0

print freq_list
n = 10
freq_list_ = [freq_list[i:i + n] for i in range(0, len(freq_list), n)]


print freq_list_
# cFile = open(os.path.join(output_path, filename), 'a')
# cFile.write('/SOL \n')
# cFile.write('!\n')
# cFile.write('FINISH \n')
# cFile.write('/SOLU \n')
# cFile.write('ANTYPE,3            ! Harmonic analysis \n')
# cFile.write('*dim, freq_list{0}, array, {1} \n'.format(sind, len(freq_list)))
# for i, freq in enumerate(freq_list_):
#     cFile.write('freq_list{0}('.format(sind) + str(i * n + 1) + ') = ' + ', '.join([str(f) for f in freq]) + '\n')
# cFile.write('HARFRQ, , , , , %freq_list{0}%, , ! Frequency range / list \n'.format(sind))