from math import sin,pi

def approximate_sin_piece_wise_linear(periods,points,start=0,timescale=2*pi):
    parts=points-1
    full_len = periods*pi*2
    part_len = full_len/parts
    pwl=[]
    for i in range(points):
        pwl.append((i*part_len/timescale,sin(i*part_len)))
    return pwl

def gen_plot_files(tuples,path_basename):
    with open(path_basename + '.data', 'wt') as f:
        f.write("\n".join([ str(i)+" "+str(j) for i,j in tuples]))
    with open(path_basename + '.gnuplot', 'wt') as f:
        f.write("\n")
        f.write("plot '"+path_basename+".data' w lines")

def gen_full_bridge_rectified_sin_wave(length,points,freq=60):
    part=approximate_sin_piece_wise_linear(1/2,points,timescale=freq*2*pi)
    ret=[]
    num_parts = int(length*freq*2)
    part_len  = length/num_parts
    for i in range(num_parts):
        ret+=[(j+(i*part_len),k) for j,k in part]
    return ret
