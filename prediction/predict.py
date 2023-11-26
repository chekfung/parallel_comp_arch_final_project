import sys
from bitarray import bitarray



# assume if read first, it is writer
def predict_write_last_time(filepath, number_of_procs):
    # Create a dictionary to store the threads that have accessed each address


    # for each cacheline (addr >> 9), store readers that read from it associated with the last thread/proc that wrote to it
    cache_line_table = {} # tracks current pattern # dictionary of  number_of_procs arrays which are each number_of_procs bits wide
    cache_line_writer = {} # tracks current/last writer
    cache_line_history = {} # tracks readers for current writer
    cache_line_prediction = {}

    # Open the file and read through each line
    with open(file_path, 'r') as file:
        for line in file:
            # Split the line into components
            components = line.split()
            # Check if the line has enough components
            if len(components) < 8:
                # Print a warning and skip this line
                # print(f"Warning: Skipping line - not enough components: {line}", file=sys.stderr)
                continue
            # print(components)
            thread = int(components[1])
            read_write = components[4]
            address = int(components[7],0)
            cache_line = address >> 9

            if read_write == 'W':
                
                # If cache_line not in cache_line_writer #first writer
                if cache_line not in cache_line_writer:
                    # add thread to cache_line_writer
                    cache_line_writer[cache_line] = thread # 1 represents first time, thus cache_line_table is empty
                else:
                # else its the next write, thus we should save the current readers for that cache_line and make prediction of readers for the new write (if that CL has been written too once)
                    if cache_line in cache_line_table and cache_line_table[cache_line][thread][number_of_procs] == 1: # check if thread has been written too before
                        # since its present, we can make prediction,
                        cache_line_prediction[cache_line] = cache_line_table[cache_line][thread]
                    
                    # update table, writer and clear CL history

                    # update cache_line_table
                    if cache_line not in cache_line_table:
                        cache_line_table[cache_line] = [bitarray([0]* (number_of_procs + 1)) for _ in range(number_of_procs)] # last bit is for presence
                        if cache_line not in cache_line_history:
                            cache_line_history[cache_line] = bitarray([0]* (number_of_procs + 1))
                        else:
                            cache_line_table[cache_line][cache_line_writer[cache_line]] = cache_line_history[cache_line]
                            cache_line_table[cache_line][cache_line_writer[cache_line]][number_of_procs] = 1 # set present field

                    # TODO: evaluate prediction accuracy
                    # use history and prediction to determine it


                    # Update writer and reset history
                    cache_line_history[cache_line] = bitarray([0]* (number_of_procs + 1))
                    cache_line_writer[cache_line] = thread 


            else: # 'R'
                if cache_line not in cache_line_writer:
                    cache_line_writer[cache_line] = thread
                if cache_line not in cache_line_history:
                    cache_line_history[cache_line] = bitarray([0]* (number_of_procs + 1))
                cache_line_history[cache_line][thread] = 1




if __name__ == "__main__":
    # Check if a file path is provided as a command-line argument
    if len(sys.argv) != 3:
        print("Usage: python script.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    num_procs = int(sys.argv[2])
    # count_memory_access(file_path)
    # unique_thread_access(file_path)
    predict_write_last_time(file_path, num_procs)