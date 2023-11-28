from collections import defaultdict

# Set the cache line size
CACHE_LINE_SIZE_LOG = 7  # Cache line of 128 bytes

# Dictionary to store history for each cache line
cache_line_history = {}

# Read the log from a file
log_file_path = 'Parallel_results/freqmine/output_mem_trace.log'  # Update this with the path to your log file
#log_file_path = "output_mem_trace_locks.log"

with open(log_file_path, 'r') as file:
    # Process each line in the log file
    for line in file:
        parts = line.split()

        if len(parts) != 8:
            # Lock data information. Skip for now :)
            continue 

        thread = parts[1]
        access_type = parts[4]
        address = parts[-1]

        # Calculate the cache line for the given address
        cache_line = int(address, 16)  >> CACHE_LINE_SIZE_LOG

        if cache_line in cache_line_history:
            last_entry = cache_line_history[cache_line][-1]
            last_thread, last_access_type = last_entry
                
            if (last_thread, last_access_type) != (thread, access_type):
                cache_line_history[cache_line].append((thread, access_type))
        else: 
            cache_line_history[cache_line] = [(thread, access_type)]

# Now have a dictionary for each cache line. 
# Now look for the pattern per cache line and generate new dictionary :)

# Write the organized history to a file
output_file_path = 'organized_history.txt'  # Update this with the desired output file path

with open(output_file_path, 'w') as output_file:
    for cache_line, history in cache_line_history.items():
        output_file.write(f"Cache Line {cache_line}: {history}\n")

readers_per_cache_line_dictionary = {}

for cache_line, history in cache_line_history.items():
    # Iterate through all cache lines
    reader_list = []
    temp_list = []

    for entry in history:
        if entry[1] == 'W':
            if len(temp_list) == 0:
                # If temp_list is empty, first occurence
                temp_list.append(entry)
            else:
                # Finish current temp list with this and then start new one
                if len(temp_list) != 1:
                    # Get rid of (Write then Write)
                    reader_list.append(temp_list)

                temp_list = []
                temp_list.append(entry)

        else:
            # Read
            if len(temp_list) == 0:
                # Check if started a entry
                continue
            
            found_thread_already = False

            # Want unique readers, but also do not include the writer thread (as a read after a write on the same thread)
            for (thread, _) in temp_list:
                if entry[0] == thread:
                    found_thread_already = True
            
            if found_thread_already:
                continue
            else:
                # Do not include if same as writer (home site would not see this read)
                temp_list.append(entry)


    readers_per_cache_line_dictionary[cache_line] = reader_list
        
# Write the organized history to a file
output_file_path = 'organized_history_output_file.txt'  # Update this with the desired output file path

with open(output_file_path, 'w') as output_file:
    for cache_line, history in readers_per_cache_line_dictionary.items():
        output_file.write(f"Cache Line {cache_line}: {history}\n")