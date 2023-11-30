import sys
from bitarray import bitarray
import copy



class MessageHistoryTable:
    def __init__(self, max_entries_per_line):
        # Dictionary to store cacheline address and corresponding history
        self.history_table = {}
        # Maximum number of entries to store per cacheline
        self.max_entries_per_line = max_entries_per_line

    def update_history(self, cacheline_address, thread_id, operation):
        # Check if cacheline exists in the history table
        if cacheline_address not in self.history_table:
            self.history_table[cacheline_address] = []

        # Enforce Coherence Protocols

        # For reads, if there is either a previous R or W, then we shouldnt add it unless...
        if operation == "R":
            for i in range(len(self.history_table[cacheline_address])-1, -1, -1): # check if this goes to 0
                entry = self.history_table[cacheline_address][i]
                e_thread_id = entry[0]
                e_op = entry[1]
                flag = False # means allow to continue
                if e_thread_id == thread_id: # Todo: we could check if its a read
                    for j in range(i, len(self.history_table[cacheline_address])): # check if this goes to 0
                        entry_1 = self.history_table[cacheline_address][j]
                        e1_id = entry_1[0]
                        e1_op = entry_1[1]
                        if e1_id != e_thread_id and e1_op == 'W':
                            flag = True
                            break 

                    if flag:
                        break
                    else: 
                        return
                    
        # For writes, if there is a previous R, then we can it, if there is a previous W, then we shouldnt add it unless...
        if operation == "W":
            for i in range(len(self.history_table[cacheline_address])-1, -1, -1): # check if this goes to 0
                entry = self.history_table[cacheline_address][i]
                e_thread_id = entry[0]
                e_op = entry[1]
                flag = False # means allow to continue
                if e_thread_id == thread_id and e_op == 'W': 
                    for j in range(i, len(self.history_table[cacheline_address])): # check if this goes to 0
                        entry_1 = self.history_table[cacheline_address][j]
                        e1_id = entry_1[0]
                        e1_op = entry_1[1]
                        if e1_id != e_thread_id and e1_op == 'W':
                            flag = True
                            break 
                    # We will return, unless we find a W from a differnt thread, then flag is set
                    if flag:
                        break
                    else: 
                        return
                    
        # Append the new tuple to the history
        self.history_table[cacheline_address].append((thread_id, operation))  # operation is either W or R

        # Keep only the latest N entries for the cacheline
        if len(self.history_table[cacheline_address]) > self.max_entries_per_line:
            self.history_table[cacheline_address].pop(0)

    def get_history(self, cacheline_address):
        # Return the history for the given cacheline address
        return copy.deepcopy(self.history_table.get(cacheline_address, []))



class PatternHistoryTable:
    def __init__(self, max_entries, number_of_procs):
        # Dictionary to store patterns indexed by tuples
        self.pattern_table = {}
        # Maximum number of entries to store in the pattern table
        self.max_entries = max_entries
        # Number of processors
        self.number_of_procs = number_of_procs


    # TODO reuse initial non complete histories
    def upgrade_index_by_pattern(self, pattern_tuple, proc_to_set, reader_used):
        # Check if pattern_tuple exists in the pattern table
        # one_less_pattern = pattern_tuple[:-1]
        # if one_less_pattern in self.pattern_table:
        #     self.pattern_table[pattern_tuple] = self.pattern_table.pop[one_less_pattern]
        # elif 
        if pattern_tuple not in self.pattern_table:
            self.pattern_table[pattern_tuple] =  bitarray([0] * self.number_of_procs * 2)
            
        # Set the value at the specified index to 1
        read = self.pattern_table[pattern_tuple][proc_to_set*2]
        confidence = self.pattern_table[pattern_tuple][proc_to_set*2 + 1]
        if reader_used:
            if read == 0 and confidence == 0:
                self.pattern_table[pattern_tuple][proc_to_set*2] = 1     # switch to read, low confidence
                # self.pattern_table[pattern_tuple][proc_to_set*2+1] = 0 # confidence stays 0
            elif read == 0 and confidence == 1:
                # self.pattern_table[pattern_tuple][proc_to_set*2] = 0   # stays not read, but low confidence
                self.pattern_table[pattern_tuple][proc_to_set*2 + 1] = 0 
            elif read == 1 and confidence == 0:
                self.pattern_table[pattern_tuple][proc_to_set*2 + 1] = 1 # stays read, but increase confidence
            # else: Stay confident in read
        else: # not_read
            if read == 0 and confidence == 0:
                # self.pattern_table[pattern_tuple][proc_to_set*2] = 0     # stays not used
                self.pattern_table[pattern_tuple][proc_to_set*2 + 1] = 1   # increase confidence
            # elif write == 0 and confidence == 1: not needed
            #     self.pattern_table[pattern_tuple][proc_to_set*2] = 0       # stays not read
                # self.pattern_table[pattern_tuple][proc_to_set*2 + 1] = 1 # stays confident
            elif read == 1 and confidence == 0:
                self.pattern_table[pattern_tuple][proc_to_set*2] = 0       # switch to not read
            elif read == 1 and confidence == 1:
                # self.pattern_table[pattern_tuple][proc_to_set*2] = 0   # stays read, but low confidence
                self.pattern_table[pattern_tuple][proc_to_set*2 + 1] = 0 


        # Remove the least frequently occurring patterns if the table exceeds the maximum entries
        if len(self.pattern_table) > self.max_entries:
            # min_pattern = min(self.pattern_table, key=lambda x: self.pattern_table[x].count())
            # del self.pattern_table[min_pattern]
            first_key = next(iter(self.pattern_table))
            del self.pattern_table[first_key]
        return pattern_tuple

    def get_pattern_info(self, pattern_tuple):
        # Return the prediction bitarray for the given pattern_tuple
        if tuple(pattern_tuple) in self.pattern_table:
            # return copy.deepcopy(self.pattern_table.get(tuple(pattern_tuple)))
            # return every even bit
            return self.pattern_table[tuple(pattern_tuple)][::2]
        else:
            return bitarray([0] * self.number_of_procs)

        # TODO: Implement the following logic
        # Return every even  bit at self.pattern_table[tuple(pattern_tuple)] but only return 1 if odd bit after is 1
        





class CachelinePatternHistoryTables:
    def __init__(self, max_entries_per_line, max_entries_per_pattern, number_of_procs):
        # Dictionary to store PatternHistoryTable instances indexed by cacheline address
        self.cacheline_pattern_tables = {}
        # Maximum number of entries to store per cacheline in the MessageHistoryTable
        self.max_entries_per_line = max_entries_per_line
        # Maximum number of entries to store in the PatternHistoryTable
        self.max_entries_per_pattern = max_entries_per_pattern

        self.number_of_procs = number_of_procs


    def set_prediction_by_history(self,cacheline, history, prediction):
        if cacheline not in self.cacheline_pattern_tables:
            self.cacheline_pattern_tables[cacheline] = PatternHistoryTable(self.max_entries_per_pattern, self.number_of_procs)
        # iterate through each bit in prediction and update the pattern table
        for i in range(len(prediction)):
            self.cacheline_pattern_tables[cacheline].upgrade_index_by_pattern(history, i, prediction[i] == 1)




    def upgrade_index_by_pattern(self, cacheline, pattern_tuple, proc_to_set, write_not_read):
        # Check if cacheline_address has a PatternHistoryTable instance
        if cacheline not in self.cacheline_pattern_tables:
            self.cacheline_pattern_tables[cacheline] = PatternHistoryTable(self.max_entries_per_pattern, self.number_of_procs)

        # Update MessageHistoryTable for the cacheline
        pattern = self.cacheline_pattern_tables[cacheline].upgrade_index_by_pattern(pattern_tuple, proc_to_set, write_not_read)
        return pattern

    def get_pattern_info_for_cacheline(self, cacheline_address, pattern_tuple):
        # Check if cacheline_address has a PatternHistoryTable instance
        if cacheline_address in self.cacheline_pattern_tables:
            # Retrieve pattern information for the given pattern_tuple
            return self.cacheline_pattern_tables[cacheline_address].get_pattern_info(pattern_tuple)
        else:
            return  bitarray([0] * number_of_procs)  # Adjust the return value to match the structure


# assume if read first, it is writer

# Pattern history table should have two bits per process, 00, 1 bit is take or no, the other is confidence
# if 00 then no prediction, if 01 then prediction is 1, if 10 then prediction is 0, if 11 then prediction is 1

def predict_readers_two_level_update_MSR(file_path, max_entries_in_mht, max_lines_per_PHT, number_of_procs, count_thread_write_as_read):
    correct = 0
    incorrect = 0
    count = 0

    pattern_tables = CachelinePatternHistoryTables(max_entries_in_mht,max_lines_per_PHT, number_of_procs)
    message_history_table = MessageHistoryTable(max_entries_in_mht)
    HistoryTracker = {}
    Cache_Predictions = {}
    cache_line_history = {} # tracks readers per cacheline for current HTracker
    cache_line_writer = {}

    last_thread = -1

    # Open the file and read through each line
    with open(file_path, 'r') as file:
        for line in file:
            components = line.split()
            if len(components) < 8:
                continue

            thread = int(components[1])
            read_write = components[4]
            address = int(components[7], 0)
            cache_line = address >> 8



            # Update History for Cacheline (add it to the MHR)
            message_history_table.update_history(cache_line, thread,read_write)

            # Get history for cacheline (fetch MHR)
            history = message_history_table.get_history(cache_line)


            # Current PHT idx
            if cache_line not in HistoryTracker:
                cache_writer_history = []
            else:
                cache_writer_history = HistoryTracker[cache_line]



            # if Read, then update the PHT for the HTracker index (tracks the index of the current writer)
                # issue, here is that eventually all procs will be set to 1 
                # (until its cycled out (LRU), we could add limit that after X are flipped, flip all back to 0)

            # if Write, then update HTracker to new PHT index

            if read_write == 'W':

                if cache_line not in cache_line_history:                
                    cache_line_history[cache_line] = bitarray([0]* (number_of_procs + 1))
                old_readers = cache_line_history[cache_line][:number_of_procs]



                # Accuracy Evaluation
                # If there is a prediction evaluate it
                if cache_line in Cache_Predictions and cache_line in cache_line_history and cache_line_history[cache_line][number_of_procs] == 1:
                    old_prediction = Cache_Predictions[cache_line]
                    thread_writer = cache_line_writer[cache_line]

                    cor = True
                    if count_thread_write_as_read == 1 or 1 << thread_writer != int(old_readers[::-1].to01(),2):
                        if old_prediction == old_readers:
                            correct += 1
                        else:
                            incorrect += 1
                            cor = False
                        print(f"{count} Predictions: {old_prediction} Readers: {old_readers} Thread: {cache_line_writer[cache_line]} CL: {cache_line} : {cor}")
                    

                    cache_line_history[cache_line] = bitarray([0]* (number_of_procs + 1))
                    
                    # Update PatternHistoryTable for the current cacheline and thread
                    pattern_tables.set_prediction_by_history(cache_line, tuple(cache_writer_history), old_readers)

                # New Prediction
                Cache_Predictions[cache_line] = pattern_tables.get_pattern_info_for_cacheline(cache_line,history)
                cache_line_writer[cache_line] = thread

                #  Update tracker
                HistoryTracker[cache_line] = message_history_table.get_history(cache_line)
            else:  # 'R'
                # Update PatternHistoryTable for the current cacheline and thread
                # if len(cache_writer_history) != 0:
                #     updated_history = pattern_tables.update_history(cache_line, tuple(cache_writer_history), thread)
                if cache_line not in cache_line_history:
                    cache_line_history[cache_line] = bitarray([0]* (number_of_procs + 1))
                cache_line_history[cache_line][thread] = 1
                cache_line_history[cache_line][number_of_procs] = 1
            count += 1
    print(correct, incorrect)






if __name__ == "__main__":
    # Check if a file path is provided as a command-line argument
    if len(sys.argv) != 6:
        print("Usage: python script.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    number_of_procs = int(sys.argv[2])
    max_entries_in_mht = int(sys.argv[3])
    max_lines_per_PHT = int(sys.argv[4])
    allow = int(sys.argv[5])
    predict_readers_two_level_update_MSR(file_path, max_entries_in_mht, max_lines_per_PHT, number_of_procs, allow)