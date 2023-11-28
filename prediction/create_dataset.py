
# Set the cache line size
CACHE_LINE_SIZE_LOG = 7  # Cache line of 128 bytes
WRITE_INTERMEDIATE_FILES = False
# Dictionary to store history for each cache line

# Read the log from a file
files = ["blacksholes", "bodytrack", "facesim", "fluidanimate", "freqmine", "raytrace", "swaptions", "vips"]
log_file_path = 'Parallel_results/{}/output_mem_trace.log'  # Update this with the path to your log file
#log_file_path = "sample_log/output_mem_trace.log"

for filename in files:
    full_log = log_file_path.format(filename)
    cache_line_history = {}

    print("Working on PARSEC benchmark: {}".format(filename))

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
                                cache_line_history[cache_line][-1] = (thread, access_type)
                        else:
                            cache_line_history[cache_line][-1] = (thread, access_type)


                    elif (last_access_type != access_type):
                        cache_line_history[cache_line].append((thread, access_type))
                    else: 
                        continue
                else:
                    # Since thread not match, we definitely want to include this one :)
                    cache_line_history[cache_line].append((thread, access_type))
            else: 
                # New cache line entry ; create a new list for this guy
                cache_line_history[cache_line] = [(thread, access_type)]

    # Now have a dictionary for each cache line. 
    # Now look for the pattern per cache line and generate new dictionary :)

    # Write the organized history to a file
    output_file_path = 'organized_history1.txt'  # Update this with the desired output file path

    if WRITE_INTERMEDIATE_FILES:
        with open(output_file_path, 'w') as output_file:
            for cache_line, history in cache_line_history.items():
                output_file.write(f"Cache Line {cache_line}: {history}\n")

    print("Finished First Pass and written to log file :)")

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
    output_file_path = 'organized_history_output_file1.txt'  # Update this with the desired output file path

    if WRITE_INTERMEDIATE_FILES:
        with open(output_file_path, 'w') as output_file:
            for cache_line, history in readers_per_cache_line_dictionary.items():
                output_file.write(f"Cache Line {cache_line}: {history}\n")

    print("Wrote to second file. Now gathering statistics :)")

    # Generate Statistics
    os_address_space_top_guess = 10000000

    # Statistics Stuff for num shared lines
    # percentage_of_cache_lines_shared    # just total amount
    # percentage_of_cache_lines_shared_os # out of shared, percentage that are OS
    # percentage_of_cache_lines_shared_program # out of shared, percentage that are program
    total_cache_lines_touched = 0
    num_shared_lines = 0
    num_os_shared_lines = 0
    num_program_shared_lines = 0

    # Statistics stuff for average number of unique readers, per query
    # num_avg_unique_readers
    # num_avg_unique_readers_program
    # num_avg_unique_readers_os

    # Count number of consumer predictions possible (length of history)
    number_of_queries = 0
    number_of_os_queries = 0
    number_of_program_queries = 0

    # For each query, predict the average amount of readers we could theoretically predict :)
    total_number_of_consumers = 0
    total_number_of_os_consumers = 0
    total_number_of_program_consumers = 0

    # Statistics stuff for average number of queries per shared cache line
    # num_avg_number_of_producer_consumer_predictions
    # num_avg_number_of_producer_consumer_predictions_program
    # num_avg_number_of_producer_consumer_predictions_os
    # These should be encapsulated above :)


    for cache_line, history in readers_per_cache_line_dictionary.items():
        total_cache_lines_touched +=1
        
        # Need to check if it is an OS line or not
        os_line = False
        if cache_line < os_address_space_top_guess:
            os_line = True
        
        # Check if it is a shared line
        history_length = len(history)

        if history_length != 0:
            num_shared_lines += 1
            number_of_queries += history_length

            if os_line:
                num_os_shared_lines +=1
                number_of_os_queries += history_length

            else:
                num_program_shared_lines +=1
                number_of_program_queries += history_length

            for prediction_query in history:
                # Each index of history, is a write, followed by a list of consumers
                temp_consumers = len(prediction_query) - 1  # need to subtract out the original write

                total_number_of_consumers += temp_consumers

                if os_line:
                    total_number_of_os_consumers += temp_consumers
                else:
                    total_number_of_program_consumers += temp_consumers

    # statistics
    # percentage_of_cache_lines_shared = (num_shared_lines / total_cache_lines_touched) * 100
    # percentage_of_cache_line_shared_os = (num_os_shared_lines / num_shared_lines) * 100
    # percentage_of_cache_lines_shared_program = (num_program_shared_lines / num_shared_lines) * 100 

    # # of the shared lines, number of average unique consumers divided by the number of predictions we could theoretically make
    # num_avg_unique_readers = total_number_of_consumers / number_of_queries
    # num_avg_unique_readers_program = total_number_of_program_consumers / number_of_program_queries
    # num_avg_uniq_readers_os = total_number_of_os_consumers / number_of_os_queries

    # # Statistics stuff for average number of queries per shared cache line
    # num_avg_number_of_producer_consumer_predictions = number_of_queries / num_shared_lines
    # num_avg_number_of_producer_consumer_predictions_program = number_of_program_queries / num_program_shared_lines
    # num_avg_number_of_producer_consumer_predictions_os = number_of_os_queries / num_os_shared_lines
    # Check if num_shared_lines is not zero before dividing to avoid divide-by-zero error
    # Calculate percentage of cache lines shared
    if total_cache_lines_touched != 0:
        percentage_of_cache_lines_shared = (num_shared_lines / total_cache_lines_touched) * 100
    else:
        percentage_of_cache_lines_shared = 0

    # Calculate percentage of cache line shared for OS and Program
    if num_shared_lines != 0:
        percentage_of_cache_line_shared_os = (num_os_shared_lines / num_shared_lines) * 100
        percentage_of_cache_lines_shared_program = (num_program_shared_lines / num_shared_lines) * 100
    else:
        percentage_of_cache_line_shared_os = 0
        percentage_of_cache_lines_shared_program = 0

    # Calculate average number of consumers per prediction
    if number_of_queries != 0:
        num_avg_number_of_producer_consumer_predictions = number_of_queries / num_shared_lines
    else:
        num_avg_number_of_producer_consumer_predictions = 0

    # Calculate average number of consumers per prediction for Program and OS
    if num_program_shared_lines != 0:
        num_avg_number_of_producer_consumer_predictions_program = number_of_program_queries / num_program_shared_lines
    else:
        num_avg_number_of_producer_consumer_predictions_program = 0

    if num_os_shared_lines != 0:
        num_avg_number_of_producer_consumer_predictions_os = number_of_os_queries / num_os_shared_lines
    else:
        num_avg_number_of_producer_consumer_predictions_os = 0

    # Calculate average unique consumers per prediction
    if number_of_queries != 0:
        num_avg_unique_readers = total_number_of_consumers / number_of_queries
    else:
        num_avg_unique_readers = 0

    if number_of_program_queries != 0:
        num_avg_unique_readers_program = total_number_of_program_consumers / number_of_program_queries
    else:
        num_avg_unique_readers_program = 0

    if number_of_os_queries != 0:
        num_avg_uniq_readers_os = total_number_of_os_consumers / number_of_os_queries
    else:
        num_avg_uniq_readers_os = 0


    output_file_path = 'run_stats_directory/run_statistics_{}.txt'.format(filename)  # Update this with the desired output file path

    with open(output_file_path, 'w') as output_file:
        output_file.write("Statistics\n")
        output_file.write(f"Shared Cache Lines (Total): {percentage_of_cache_lines_shared}%\n")
        output_file.write(f"Shared Cache Lines (Program): {percentage_of_cache_lines_shared_program}%\n")
        output_file.write(f"Shared Cache Lines (OS): {percentage_of_cache_line_shared_os}%\n")

        output_file.write(f"Average Unique Consumers per Prediction (Total): {num_avg_unique_readers}\n")
        output_file.write(f"Average Unique Consumers per Prediction (Program): {num_avg_unique_readers_program}\n")
        output_file.write(f"Average Unique Consumers per Prediction (OS) {num_avg_uniq_readers_os}\n")

        output_file.write(f"Average Queries per Shared Cache Line (Total): {num_avg_number_of_producer_consumer_predictions}\n")
        output_file.write(f"Average Queries per Shared Cache Line (Program): {num_avg_number_of_producer_consumer_predictions_program}\n")
        output_file.write(f"Average Queries per Shared Cache Line (OS): {num_avg_number_of_producer_consumer_predictions_os}\n")

        # -------------

        output_file.write("\n\nRaw Counters\n")
        output_file.write(f"total_cache_lines_touched: {total_cache_lines_touched}\n")
        output_file.write(f"num_shared_lines: {num_shared_lines}\n")
        output_file.write(f"num_os_shared_lines: {num_os_shared_lines}\n")
        output_file.write(f"num_program_shared_lines: {num_program_shared_lines}\n")

        # Statistics stuff for average number of unique readers, per query
        output_file.write(f"num_avg_unique_readers: {num_avg_unique_readers}\n")
        output_file.write(f"num_avg_unique_readers_program: {num_avg_unique_readers_program}\n")
        output_file.write(f"num_avg_unique_readers_os: {num_avg_uniq_readers_os}\n")

        # Count number of consumer predictions possible (length of history)
        output_file.write(f"number_of_queries: {number_of_queries}\n")
        output_file.write(f"number_of_os_queries: {number_of_os_queries}\n")
        output_file.write(f"number_of_program_queries: {number_of_program_queries}\n")

        # For each query, predict the average amount of readers we could theoretically predict :)
        output_file.write(f"total_number_of_consumers: {total_number_of_consumers}\n")
        output_file.write(f"total_number_of_os_consumers: {total_number_of_os_consumers}\n")
        output_file.write(f"total_number_of_program_consumers: {total_number_of_program_consumers}\n")