import argparse

# Create the parser
parser = argparse.ArgumentParser(description='Compare lines in two files.')
parser.add_argument('file1', help='First file name')
parser.add_argument('file2', help='Second file name')

# Parse the arguments
args = parser.parse_args()

# Read lines from both files
with open(args.file1, 'r') as f:
    lines1 = set(line.strip() for line in f)
with open(args.file2, 'r') as f:
    lines2 = set(line.strip() for line in f)

# Find lines in file1 that are not in file2
diff_lines = lines1 - lines2

# Print the count and the different lines
print(f'Number of different lines: {len(diff_lines)}')
for line in diff_lines:
    print(line)
