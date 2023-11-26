import sys
from bitarray import bitarray


class MessageHistoryTable:
    def __init__(self, max_entries_per_line=10):
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
            for i in range(len(self.history_table[cacheline_address])-1, 1, -1): # check if this goes to 0
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
            for i in range(len(self.history_table[cacheline_address])-1, 1, -1): # check if this goes to 0
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
            self.history_table[cacheline_address] = self.history_table[cacheline_address][-self.max_entries_per_line:]

    def get_history(self, cacheline_address):
        # Return the history for the given cacheline address
        return self.history_table.get(cacheline_address, [])


# # Example Usage:
# history_table = MessageHistoryTable()

# # Update history for cacheline 0x100 with thread_id=1 and operation='R'
# history_table.update_history(0x100, 1, 'R')

# # Update history for cacheline 0x100 with thread_id=2 and operation='W'
# history_table.update_history(0x100, 2, 'W')

# # Retrieve history for cacheline 0x100
# print(history_table.get_history(0x100))

class PatternHistoryTable:
    def __init__(self, max_entries=100, num_procs=8):
        # Dictionary to store patterns indexed by tuples
        self.pattern_table = {}
        # Maximum number of entries to store in the pattern table
        self.max_entries = max_entries
        # Number of processors
        self.num_procs = num_procs

    def update_pattern(self, pattern_tuple, index_to_set=0):
        # Check if pattern_tuple exists in the pattern table
        one_less_pattern = pattern_tuple[:-1]
        if one_less_pattern in self.pattern_table:
            self.pattern_table[pattern_tuple] = self.pattern_table.pop[one_less_pattern]
        elif pattern_tuple not in self.pattern_table:
            self.pattern_table[pattern_tuple] = {'prediction': bitarray([0] * self.num_procs)}
            
        # Set the value at the specified index to 1
        self.pattern_table[pattern_tuple]['prediction'][index_to_set] = 1
        # TODO: ??? If prediction has more than half? predictions, set to 0

        # Remove the least frequently occurring patterns if the table exceeds the maximum entries
        if len(self.pattern_table) > self.max_entries:
            min_pattern = min(self.pattern_table, key=lambda x: self.pattern_table[x]['prediction'].count())
            del self.pattern_table[min_pattern]

    def get_pattern_info(self, pattern_tuple):
        # Return the prediction bitarray for the given pattern_tuple
        return self.pattern_table.get(pattern_tuple, {'prediction': bitarray([0] * self.num_procs)})['prediction']


# # Example Usage:
# pattern_table = PatternHistoryTable()

# # Use the same tuples as in MessageHistoryTable
# tuple1 = (1, 'R')
# tuple2 = (2, 'W')

# # Update pattern for tuple1 with prediction 0b110 (for example)
# pattern_table.update_pattern(tuple1, 0b110)

# # Update pattern for tuple2 with prediction 0b101 (for example)
# pattern_table.update_pattern(tuple2, 0b101)

# # Retrieve information for tuple1
# print(pattern_table.get_pattern_info(tuple1))


class CachelinePatternHistoryTables:
    def __init__(self, max_entries_per_line=10, max_entries_per_pattern=100):
        # Dictionary to store PatternHistoryTable instances indexed by cacheline address
        self.cacheline_pattern_tables = {}
        # Maximum number of entries to store per cacheline in the MessageHistoryTable
        self.max_entries_per_line = max_entries_per_line
        # Maximum number of entries to store in the PatternHistoryTable
        self.max_entries_per_pattern = max_entries_per_pattern


    def update_history(self, cacheline_address, history, prediction_id):
        # Check if cacheline_address has a PatternHistoryTable instance
        if cacheline_address not in self.cacheline_pattern_tables:
            self.cacheline_pattern_tables[cacheline_address] = PatternHistoryTable(max_entries=self.max_entries_per_pattern)

        # Update MessageHistoryTable for the cacheline
        self.cacheline_pattern_tables[cacheline_address].update_pattern(history, prediction_id)

    def get_pattern_info_for_cacheline(self, cacheline_address, pattern_tuple):
        # Check if cacheline_address has a PatternHistoryTable instance
        if cacheline_address in self.cacheline_pattern_tables:
            # Retrieve pattern information for the given pattern_tuple
            return self.cacheline_pattern_tables[cacheline_address].get_pattern_info(pattern_tuple)
        else:
            return {'prediction': bitarray([0] * num_procs)}  # Adjust the return value to match the structure


# # Example Usage:
# cacheline_pattern_table = CachelinePatternHistoryTables()

# # Update history and pattern for cacheline 0x100
# cacheline_pattern_table.update_history_and_pattern(0x100, 1, 'R', 0b110)
# cacheline_pattern_table.update_history_and_pattern(0x100, 2, 'W', 0b101)

# # Retrieve pattern information for cacheline 0x100 and tuple (1, 'R')
# print(cacheline_pattern_table.get_pattern_info_for_cacheline(0x100, (1, 'R')))

class MessageHistoryTables:
    def __init__(self):
        # Dictionary to store MessageHistoryTable instances indexed by cacheline address
        self.message_history_tables = defaultdict(MessageHistoryTable)

    def update_history(self, cacheline_address, thread_id, operation):
        # Update MessageHistoryTable for the cacheline
        self.message_history_tables[cacheline_address].update_history(thread_id, operation)

    def get_history_for_cacheline(self, cacheline_address):
        # Retrieve message history for the given cacheline address
        return self.message_history_tables[cacheline_address].get_history()





# assume if read first, it is writer

def predict_readers_two_level(file_path, number_of_procs):
    correct = 0
    incorrect = 0

    pattern_tables = CachelinePatternHistoryTables()
    message_history_tables = MessageHistoryTables()
    HistoryTracker = {}
    Cache_Predictions = {}

    # Open the file and read through each line
    with open(file_path, 'r') as file:
        for line in file:
            components = line.split()
            if len(components) < 8:
                continue

            thread = int(components[1])
            read_write = components[4]
            address = int(components[7], 0)
            cache_line = address >> 9

            # Update History for Cacheline (add it to the MHR)
            message_history_tables.update_history(cache_line, thread,read_write)

            # Get history for cacheline (fetch MHR)
            history = message_history_tables.get_history_for_cacheline(cache_line)

            # Current PHT idx
            cache_writer_history = HistoryTracker[cache_line]

            # if Read, then update the PHT for the HTracker index (tracks the index of the current writer)
                # issue, here is that eventually all procs will be set to 1 
                # (until its cycled out (LRU), we could add limit that after X are flipped, flip all back to 0)

            # if Write, then update HTracker to new PHT index

            # Get prediction from pattern_tables

            if read_write == 'W':
                HistoryTracker[cache_line] = message_history_tables[cache_line]
                Cache_Predictions[cache_line] = pattern_tables.get_pattern_info_for_cacheline(cache_line,history)

            else:  # 'R'
                # Update PatternHistoryTable for the current cacheline and thread
                pattern_tables.update_history(cache_line, cache_writer_history, thread)
                # TODO: Track Predictions vs reality 
                # Use cacheline_history and pattern prediction to determine accuracy

    # TODO: Add the evaluation of prediction accuracy

            


    #         if read_write == 'W':
    #             if cache_line in pattern_tables.cacheline_pattern_tables:
    #                 pattern_info = pattern_tables.get_pattern_info_for_cacheline(cache_line, (thread, 'R'))
    #                 if pattern_info['prediction'] == thread:
    #                     correct += 1
    #                 else:
    #                     incorrect += 1

    #             pattern_tables.update_history_and_pattern(cache_line, thread, 'W', thread)

    #         else:  # 'R'
    #             if cache_line not in pattern_tables.cacheline_pattern_tables:
    #                 pattern_tables.update_history_and_pattern(cache_line, thread, 'R', 0)  # 0 as placeholder prediction
    #             else:
    #                 pattern_info = pattern_tables.get_pattern_info_for_cacheline(cache_line, (thread, 'R'))
    #                 if pattern_info['prediction'] == thread:
    #                     correct += 1
    #                 else:
    #                     incorrect += 1

    # print(f"Correct {correct}, Incorrect {incorrect}")




if __name__ == "__main__":
    # Check if a file path is provided as a command-line argument
    if len(sys.argv) != 3:
        print("Usage: python script.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    num_procs = int(sys.argv[2])
    # count_memory_access(file_path)
    # unique_thread_access(file_path)
    predict_readers_two_level(file_path, num_procs)