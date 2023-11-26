import sys

def count_memory_access(file_path):
    # Create dictionaries to store the counts of each address for reads and writes
    read_counts = {}
    write_counts = {}
    total_counts = {}
    

    # Open the file and read through each line
    with open(file_path, 'r') as file:
        for line in file:
            # Split the line into components
            components = line.split()
            # print(components)

            # Check if the line has enough components
            if len(components) < 7:
                # Print a warning and skip this line
                print(f"Warning: Skipping line - not enough components: {line}", file=sys.stderr)
                continue

            # Extract the access type and address from the line
            access_type = components[4]
            # Remove the "ADDR:" prefix from the address
            address_line = components[7]

            # Update the count in the appropriate dictionary
            if access_type == 'R':
                read_counts[address_line] = read_counts.get(address_line, 0) + 1
            elif access_type == 'W':
                write_counts[address_line] = write_counts.get(address_line, 0) + 1
            total_counts[address_line] = total_counts.get(address_line, 0) + 1
    # Print the results for reads
    print("Reads:")
    for address, count in read_counts.items():
        print(f"Address {address} is read {count} times.")

    # Print the results for writes
    print("\nWrites:")
    for address, count in write_counts.items():
        print(f"Address {address} is written {count} times.")

    # Print sum of results
    print("Total Accesses:")
    for address, count in total_counts.items():
        print(f"Address {address} is written {count} times.")

def unique_thread_access(file_path):
    # Create a dictionary to store the threads that have accessed each address
    address_threads = {}

    # Open the file and read through each line
    with open(file_path, 'r') as file:
        for line in file:
            # Split the line into components
            components = line.split()
            # print(components)

            # Check if the line has enough components
            if len(components) < 8:
                # Print a warning and skip this line
                # print(f"Warning: Skipping line - not enough components: {line}", file=sys.stderr)
                continue

            # Extract the thread ID and address from the line
            thread_id = components[1]
            address_line = components[7]

            # Update the set of threads that have accessed the address
            if address_line in address_threads:
                address_threads[address_line].add(thread_id)
            else:
                address_threads[address_line] = {thread_id}

    number_of_shared_lines = 0
    number_of_single_lines = 0
    # Print the results
    for address, threads in address_threads.items():
        if len(threads) > 1:
            number_of_shared_lines = number_of_shared_lines + 1
        else:
            number_of_single_lines += 1
        print(f"Address {address} is accessed by threads: {', '.join(threads)}")

    # print total count
    # count_shared_addresses = sum(len(address_threads[address]) > 1 for address in address_threads)

    print(f"Number of shared lines: {number_of_shared_lines}")
    print(f"Number of single lines: {number_of_single_lines}")

def calc_unique_reads(file_path):
    # Create a dictionary to store the threads that have accessed each address
    address_threads = {}

    # Open the file and read through each line
    with open(file_path, 'r') as file:
        for line in file:
            # Split the line into components
            components = line.split()
            # print(components)

            # Check if the line has enough components
            if len(components) < 8:
                # Print a warning and skip this line
                # print(f"Warning: Skipping line - not enough components: {line}", file=sys.stderr)
                continue

            # Extract the thread ID and address from the line
            thread_id = components[1]
            address_line = components[7]
            read_write = components[4]

            # Update the set of threads that have accessed the address
            if address_line in address_threads:
                # // not sure what do to for reads before write (assumes homesite) TODO: determine homesite
                addr_list = address_threads[address_line]
                old_id = address_threads[address_line][1]
                if thread_id == old_id: # ignore read/writes from same thread
                    continue
                    
                if read_write == 'W':
                    empty_set = set()
                    address_threads[address_line] = ['W', thread_id, empty_set,addr_list[3] + len(addr_list[2]),addr_list[4] + (int)(addr_list[0] == 'W')]
                else: # read_write is 'R
                    address_threads[address_line][2].add(thread_id)


            else: # not in bag: key: addr, value: {R/W, ThreadiD,{thrads that have read}}
                address_threads[address_line] = ['F', thread_id,set(),0,0] # F for first, we dont want to count first write

    for address, read_list in address_threads.items():
        if read_list[3] + len(read_list[2]) != 0 or read_list[4] + (read_list[0] == 'W') != 0:
            print(f"Address {address} was read a total of {read_list[3] + len(read_list[2])} unique times and written by different threads a total of {read_list[4] + (read_list[0] == 'W')} times")


if __name__ == "__main__":
    # Check if a file path is provided as a command-line argument
    if len(sys.argv) != 2:
        print("Usage: python script.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    # count_memory_access(file_path)
    # unique_thread_access(file_path)
    calc_unique_reads(file_path)