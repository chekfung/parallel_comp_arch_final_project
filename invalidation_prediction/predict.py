
# goal is to predict invalidations for an output log
# if our processor has an address (that we have previously read from)
    # we need to predict when to invalidate this address before another processor writes to it

# TODO:
# 1. read in the output log and clean changing WR to RWITM
# 2. Seperate instruction stream by thread; make sure my processor cannot see others information
# 3. Create a dictionary of addresses and their last access time (time can be by instruction number)

# A RWITM on Proc A means that we are reading from the same address that is located on another processor (Proc B)
# We need to predict when to invalidate this address from Proc B before Proc A writes to it

import sys
import re

# Clean the output log
def clean_output_log(file_path):
    # Open the file and read through each line
    new_read = 0
    new_thread = 0
    new_cache_line = 0
    new_line = 0
    with open("cleaned_output_log.txt", 'w+') as new_file:
        with open(file_path, 'r') as file:
            for line in file:
                
                # Split the line into components
                components = line.split()
                # Check if the line has enough components
                if len(components) < 7:
                    # skip this line
                    continue
                # print(components)
                thread = int(components[1])
                read_write = components[4]
                address = int(components[7],0)
                cache_line = address >> 8

                if read_write == 'R': # sets flag for next line
                    new_thread = thread
                    new_cache_line = cache_line
                    new_line = line
                    print(new_line)
                    new_read = 1
                
                elif read_write == 'W' and new_read == 1 and cache_line == new_cache_line and thread == new_thread: # if we are reading from same address and we have a flag
                    # RWITM encountered
                    new_read = 0
                    # write line to new file and delete read line
                    new_file.write(line)
                else:
                    # write new_line and line to new file
                    if new_read == 1:
                        new_read = 0
                        new_file.write(new_line)
                    new_file.write(line)
                    
# lets observe shared memory accesses between threads from cleaned_output_log.txt
# shared memory dictionary
shared_mem = {}
def observe_shared_memory_accesses(file_path):
    # Open the file and read through each line
    with open(file_path, 'r') as file:
        for line in file:
            # Split the line into components
            components = line.split()
            # Check if the line has enough components
            if len(components) < 7:
                # skip this line
                continue
            # print(components)
            thread = int(components[1])
            read_write = components[4]
            address = int(components[7],0)
            cache_line = address >> 8

            # create dictionary with address as key and neach processor that has accessed it as a tuple
            # if address is not in dictionary, add it with value 1
            if address not in shared_mem:
                shared_mem[address] = [thread]
            elif address in shared_mem:
                shared_mem[address].append(thread)
    
    # clean up dictionary
    # if only one processor has accessed the address, remove it from dictionary
    for key, value in shared_mem.items():
        counter = len(value)
        count = 0
        for i in range(len(value)):
            if value[0] == value[i]:
                count += 1
        if counter == count:
            shared_mem[key] = []

# find invalidations in cleaned_output_log.txt
# invalidations are when a processor reads from the same address that another processor has written to so this will be in shared_mem dictionary
# Goal is to determine when to invalidate an address from a processor
# This can be determined by finding when it is accessed by another processor
result = {}
def find_invalidates(file_path):
    # Open file and read through each line, stating where the invalidates are, what access number it is, and what processor it is on
    with open(file_path, 'r') as file:
        for line in file:
            # Split the line into components
            components = line.split()

            # save list enclosed in double brackets (components[3:]) as a list
            list_of_components = components[3:]
            print(list_of_components)

            

if __name__ == "__main__":
    # Check if a file path is provided as a command-line argument
    # if len(sys.argv) != 3:
    #     print("Usage: python3 predict.py <file_path> num_procs")
    #     sys.exit(1)

    # file_path = sys.argv[1]
    # num_procs = int(sys.argv[2])

    # #clean_output_log(file_path)
    # observe_shared_memory_accesses("cleaned_output_log.txt")

    # for key, value in shared_mem.items():
    #     if len(value) > 1:
    #         print(f"{key}: {value}")
    
    find_invalidates("organized_history.txt")
    