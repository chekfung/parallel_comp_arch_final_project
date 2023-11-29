
# Set the cache line size
CACHE_LINE_SIZE_LOG = 7  # Cache line of 128 bytes
WRITE_INTERMEDIATE_FILES = True
# Dictionary to store history for each cache line

# Read the log from a file
log_file_path = "parallel_comp_arch_final_project/sample_log/output_mem_trace.log"

full_log = log_file_path
cache_line_history = {}

def parse_files(full_log):
    with open(full_log, 'r') as file:
        # Process each line in the log file
        for line in file:
            # Go through each line :)
            parts = line.split()

            if len(parts) != 8:
                # Lock data information. Skip for now :)
                continue 

            thread = parts[1]
            access_type = parts[4]
            address = parts[-1]

            # Calculate the cache line for the given address
            cache_line = int(address, 16)  >> CACHE_LINE_SIZE_LOG
            print(access_type)

            if cache_line in cache_line_history:
                last_entry = cache_line_history[cache_line][-1]
                last_thread, last_access_type = last_entry

                if (thread == last_thread):
                    # Check if last request on this line is a RWITM (This is shown as a read, then a write on the same guy immediately following :)
                    if (last_access_type == 'R' and access_type == 'W'):
                        # If this is the case, just replace with a write (implied read with intent to modify)
                        # Otherwise, will make it seem as if there are dependent reads, when they are really just read with intent to modify to get access to everything
                        if len(cache_line_history[cache_line]) > 1:
                            # Check if previous was a write :)
                            second_last = cache_line_history[cache_line][-2]

                            if (second_last[1] == 'W'):
                                # If write twice in a row (RWRW), it should just become (W) as that is what the home site would see :)
                                cache_line_history[cache_line].pop()
                            else:
                                cache_line_history[cache_line][-1] = [thread, access_type]
                        else:
                            cache_line_history[cache_line][-1] = [thread, access_type]


                    elif (last_access_type != access_type):
                        cache_line_history[cache_line].append([thread, access_type])
                    else: 
                        continue
                else:
                    # if its a write to a new thread, mark this as invalid on the other thread
                    if access_type == 'W':
                        cache_line_history[cache_line].append("INVALIDATE")
                        cache_line_history[cache_line].append([last_thread, 'I'])
                    # Since thread not match, we definitely want to include this one :)
                    cache_line_history[cache_line].append([thread, access_type])
            else: 
                # New cache line entry ; create a new list for this guy
                cache_line_history[cache_line] = [[thread, access_type]]

    # Now have a dictionary for each cache line. 
    # Now look for the pattern per cache line and generate new dictionary :)

    # Write the organized history to a file
    output_file_path = 'organized_history.txt'  # Update this with the desired output file path

    if WRITE_INTERMEDIATE_FILES:
        with open(output_file_path, 'w') as output_file:
            for cache_line, history in cache_line_history.items():
                output_file.write(f"Cache Line {cache_line}: {history}\n")

    print("Finished First Pass and written to log file :)")


def find_invalidates():
    # find where invalidtes are
    for cache_line, history in cache_line_history.items():
        if len(history) > 1:
            for i in range(len(history)):
                counter = 0
                # count how many accesses on processor with an I
                if history[i][1] == 'I':
                    counter = 0
                    print(f"Found an invalidate at {cache_line} on processor {history[i][0]} after {i} accesses on that processor")



if __name__ == "__main__":
    parse_files(full_log)
    find_invalidates()