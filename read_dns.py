import dns.zone

def read_file_content(file_path):
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
        return file_content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def remove_lines_with_pattern(file_content, pattern):
    try:
        lines = file_content.split('\n')
        filtered_lines = [line for line in lines if pattern not in line]
        return '\n'.join(filtered_lines)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Example usage
file_path = "LOOM/ruddy.db"  # Change this to the path of your file
file_content = read_file_content(file_path)
modified_file_content = remove_lines_with_pattern(file_content, "$TTL")
zone = dns.zone.from_text(modified_file_content, origin="", relativize=False)

for name, node in zone.nodes.items():
    for rdataset in node.rdatasets:
        for rdata in rdataset:
            print(f"{name} {rdataset.rdclass} {rdataset.rdtype} {rdataset.ttl} {rdata}")