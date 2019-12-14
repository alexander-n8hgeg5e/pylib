
def split_file_on_sep(input_file_path,sep=b'\x00\x00', reverse=True):
    output_data_list=[]
    output=b''
    data=b''
    with open(input_file_path,mode='rb') as f:
        data+=f.read(1024)
        while data:
            pos=data.find(sep)
            if pos == -1:
                output+=data
                data=b''
            else:
                output+=data[:pos]
                data=data[pos+len(sep):]
                if len(output) > 0:
                    output_data_list.append(output)
                    output=b''
        
    for i in range(len(output_data_list)):
        part_file_path = input_file_path+"_" +str(i)
        with open(part_file_path,mode='wb') as f:
            if reverse:
                f.write(output_data_list[-i-1])
            else:
                f.write(output_data_list[i])
