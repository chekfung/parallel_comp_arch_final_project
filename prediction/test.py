import sys

def clean_file(file_path, new_file_path):
    # Create a dictionary to store the threads that have accessed each address
    address_threads = {}

    # Open the file and read through each line
    with open(file_path, 'r') as file:
        with open(new_file_path, "w") as file_out:

            
            previous_line = file.readline()
            last_line = ""



            

            for line in file:
                # Split the line into components
                prev_comp = previous_line.split()
                components = line.split()

                if(len(components) < 8):
                    continue

                thread_id = prev_comp[1]
                cache_line = int(prev_comp[7],0) >> 8
                read_write = prev_comp[4]

                if cache_line in address_threads:
                    # // not sure what do to for reads before write (assumes homesite) TODO: determine homesite
                    current_writer = address_threads[cache_line]
                    if thread_id == current_writer: # ignore read/writes from same thread
                        previous_line = line
                        continue
                        
                    if read_write == 'W':
                        address_threads[cache_line] = thread_id
                        # empty_set = set()
                        # address_threads[cache_line] = ['W', thread_id, empty_set,addr_list[3] + len(addr_list[2]),addr_list[4] + (int)(addr_list[0] == 'W')]
                    # else: # read_write is 'R
                        # address_threads[cache_line][2].add(thread_id)
                else: # not in bag: key: addr, value: {R/W, ThreadiD,{thrads that have read}}
                    address_threads[cache_line] = thread_id # F for first, we dont want to count first write




                if prev_comp[1] == components[1] and prev_comp[7] == components[7] and prev_comp[4] == 'R' and components[4] == 'W':
                    #  dont print previous line
                    previous_line = line
                else:
                     file_out.write(previous_line)
                previous_line = line
                last_line = line
            file_out.write(previous_line)


            
            
                 
            


if __name__ == "__main__":

    file_path = sys.argv[1]
    new_file_path = sys.argv[2]
    clean_file(file_path, new_file_path)