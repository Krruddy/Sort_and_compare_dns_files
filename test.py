def check_duplicates(filename):
    entries = {}
    line_number = 1
    duplicates_found = False
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line in entries:
                    duplicates_found = True
                    print(f"Duplicate entry '{line}' found on lines {entries[line]} and {line_number}.")
                else:
                    entries[line] = line_number
                line_number += 1
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return
    if not duplicates_found:
        print("There are no duplicate entries in the DNS file.")

# Use the function
check_duplicates('your_dns_file.txt')
