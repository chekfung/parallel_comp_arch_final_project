import sys

def count_memory_access(file_path):
    # Create dictionaries to store the counts of each address for reads and writes
    read_counts = {}
    write_counts = {}

    # Open the file and read through each line
    with open(file_path, 'r') as file:
        for line in file:
            # Split the line into components
            components = line.split()
            # print(components)

            # Check if the line has enough components
            if len(components) < 7:
                # Print a warning and skip this line
                print(f"Warning: Skipping line - not enough components: {line}")
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

    # Print the results for reads
    print("Reads:")
    for address, count in read_counts.items():
        print(f"Address {address} is read {count} times.")

    # Print the results for writes
    print("\nWrites:")
    for address, count in write_counts.items():
        print(f"Address {address} is written {count} times.")

if __name__ == "__main__":
    # Check if a file path is provided as a command-line argument
    if len(sys.argv) != 2:
        print("Usage: python script.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    count_memory_access(file_path)
