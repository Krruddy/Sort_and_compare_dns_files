import re
import ipaddress
import os
import sys
import logging
import errno

# This program increments the number of line 3, removes the duplicates and sorts based on IP addresses the DNS entries. 
# This program does not delete the old file, it renames it with the extension ".old" and creates a new file with the same name as the old one.
# For the program to work, the following conditions must be met:
# - The number that has to be incremented must be in the third line of the file.
# - The only ip addresses present in the standard DNS file must be part of the DNS entries. 
# - The only ip addresses (with the patern "XXX.XXX") present in the reverse DNS must be part of the DNS entries.
# - The name of the reverse DNS file must look like this "XXX.XXX.db" otherwise the program will consider it as a standard DNS file.


# Custom formatter class
class CustomFormatter(logging.Formatter):
    FORMATS = {
        logging.INFO: "[+] %(message)s",
        logging.WARNING: "[!] %(message)s",
        logging.ERROR: "[-] %(message)s",
    }

    def format(self, record):
        log_format = self.FORMATS.get(record.levelno, self._style._fmt)
        self._style._fmt = log_format
        return super().format(record)

# Create a logger
logger = logging.getLogger("my_logger")

# Create a StreamHandler and set the custom formatter
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())

# Add the handler to the logger
logger.addHandler(handler)

# Set the logging level
logger.setLevel(logging.INFO)

# a class named DNS_file that takes the name of the file.
class DNS_file:
    # The constructor takes the name of the file and sets the type of file, the file content, the space before the incrementation value, the incrementation value and the list of DNS entries.
    def __init__(self, name: str): 
        self.name = name
        self.type = self.find_file_type(self.name)
        self.file_content = self.set_file_content(self.name)
        self.space_before_incre_value = self.find_space_before_incre_value(self.file_content[2])
        self.incre_value = self.find_incre_value(self.file_content[2])
        self.list_of_DNS_entries = self.set_list_of_DNS_entries(self.file_content)

    # a function named find_file_type that takes the name of the file and returns the type of file (standard DNS or reverse DNS)      
    def find_file_type(self, name_of_file: str, rev_pattern = r"\d{1,3}\.db$"):
        if re.search(rev_pattern, name_of_file) == None:
            return "standard DNS"
        else:
            return "reverse DNS"
        
    # a function named set_file_content that takes the name of the file and returns the content of the file in a list
    def set_file_content(self, name_of_file: str):
        file = open(f"{name_of_file}", "r")
        return file.readlines()
    
    # a functionn named find_space_before_incre_value that takes the line containing the value to increment and returns the amount of spaces before the value to increment
    def find_space_before_incre_value(self, incre_value_line: str):
        amount_of_spaces = incre_value_line.count(' ') - 1
        return amount_of_spaces
        
    # a function named find_incre_value that takes the line containing the value to increment and returns the value to increment
    def find_incre_value(self, incre_value_line: str):
        incre_value = re.findall(r'\d+', incre_value_line)
        if len(incre_value) == 0:
            logger.error(f"Could not find the value to increment in {self.name}.")
            logger.error(f"Exiting the program.")
            sys.exit(errno.ENOENT)
        elif len(incre_value) > 1:
            logger.warning(f"Found more than one value to increment in {self.name}.")
            return int(incre_value[0])
        else:
            return int(incre_value[0])

    # a function named set_list_of_DNS_entries that takes self, the file content and returns a list of DNS entries
    def set_list_of_DNS_entries(self, file_content: list):
        if self.type == "standard DNS":
            return self.set_list_of_standard_DNS_entries(file_content)
        else:
            return self.set_list_of_reverse_DNS_entries(file_content)

    def set_list_of_standard_DNS_entries(self, file_content: list):
        list_of_DNS_entries = [line for line in file_content if self.find_ip_in_line(line) != None]
        return list_of_DNS_entries

    def set_list_of_reverse_DNS_entries(self, file_content: list):
        list_of_DNS_entries = [line for line in file_content if self.find_reverse_ip_in_line(line) != None]        
        return list_of_DNS_entries

    # a function named find_ip_in_line that determines if there is an ip address in the line and returns the match
    def find_ip_in_line(self, line: str, ip_pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"):
        match = re.search(ip_pattern, line)
        return match
    
    # a function named find_reverse_ip_in_line that determines if there is a reverse ip address in the line and returns the match
    def find_reverse_ip_in_line(self, line: str, ip_pattern = r"\d{1,3}\.\d{1,3}"):
        match = re.search(ip_pattern, line)
        return match

    # a function named increment_incre_value that increments the value to increment
    def increment_incre_value(self):
        self.incre_value += 1
    
    # a function named delete_duplicate_entries that deletes the duplicate entries
    def delete_duplicate_entries(self):
        self.list_of_DNS_entries = list(set(self.list_of_DNS_entries))

    def sort_DNS_entries(self):
        if self.type == "standard DNS":
            self.sort_standard_DNS_entries()
        else:
            self.sort_reverse_DNS_entries()

    # a function named sort_standard_DNS_entries that sorts the standard DNS entries
    def sort_standard_DNS_entries(self):
        list_of_ip = [re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", line) for line in self.list_of_DNS_entries]
        list_of_ip = [item for sublist in list_of_ip for item in sublist] 
        sorted_list_of_ip = sorted(list_of_ip, key = ipaddress.IPv4Address)
        sorted_DNS_entries = []
        for ip in sorted_list_of_ip:
            for DNS_entry in self.list_of_DNS_entries:
                if ip in DNS_entry:
                    sorted_DNS_entries += [DNS_entry]
        self.list_of_DNS_entries = sorted_DNS_entries
     
    # a function named sort_reverse_DNS_entries that sorts the reverse DNS entries   
    def sort_reverse_DNS_entries(self):
        list_of_ip = [re.findall(r"\d{1,3}\.\d{1,3}", line) for line in self.list_of_DNS_entries]
        list_of_ip = [item for sublist in list_of_ip for item in sublist] # list of ip is a list of lists, this line flattens the list
        sorted_list_of_ip = sorted(list_of_ip, key=lambda ip: [int(octet) for octet in ip.split('.')])
        
        sorted_DNS_entries = []
        for ip in sorted_list_of_ip:
            for DNS_entry in self.list_of_DNS_entries:
                if ip in DNS_entry:
                    sorted_DNS_entries += [DNS_entry]
        self.list_of_DNS_entries = sorted_DNS_entries    

    # a function named reconstruct_file that reconstructs the file with the new incrementation value and the sorted DNS entries
    def reconstruct_file(self):
        # Reconstructs the 2nd line
        reconstructed_line = self.reconstruct_line(self.space_before_incre_value, self.incre_value)
        
        # Open the file
        final_DNS_file = self.create_tmp_file(f"{self.name}")
        
        # Add the lines to the file that aren't the DNS entries
        for index, line in enumerate(self.file_content):
            if  index == 2:
                final_DNS_file.write(reconstructed_line)
            elif self.find_ip_in_line(line) == None and self.find_reverse_ip_in_line(line) == None:
                final_DNS_file.write(line)
                
        # Add the sorted DNS entries
        for line in self.list_of_DNS_entries:
            final_DNS_file.write(line)
            
        # Close the file
        final_DNS_file.close()
        
        return 0
    
    def create_tmp_file(self, name: str):
        try:
            logger.info(f"Creating the file {name}.tmp ...")
            return open(f"{name}.tmp", "x")
        except FileExistsError:
            logger.warning(f"The file {name}.tmp already exists and is going to be overwritten.")
            # clear the file
            file = open(f"{name}.tmp","r+")
            file.truncate(0)
            file.close()
            
            return open(f"{name}.tmp", "w")

    # a function named reconstruct_line that takes the amount of spaces and the incremented value and returns the line
    def reconstruct_line(self, amount_of_spaces: int, incremented_value: int):
        reconstructed_line = ""
        for i in range(amount_of_spaces): #(Is there a way to do this in one line ?)
            reconstructed_line+=' '
        reconstructed_line += str(incremented_value) + " ;\n"
        return reconstructed_line
     
    # a function named replace_file that takes the name of the file and replaces the old file with the new one
    def replace_file(self):
        #os.remove(f"{self.name}")
        os.rename(f"{self.name}", f"{self.name}.old")
        os.rename(f"{self.name}.tmp", f"{self.name}")



logger.info("Starting the program.")

# creates a list of DNS_files
DNS_files = []
amount_of_files = len(sys.argv) - 1
logger.info(f"{amount_of_files} files have been passed as arguments.")

# populates the list of DNS_files
logger.info(f"-----------------------------")
logger.info(f"Populating the DNS list ...")
for index, file in enumerate(sys.argv):
    if index != 0:
        logger.info(f"adding {file} to the list of DNS files ...")
        DNS_files += [DNS_file(file)]
logger.info(f"-----------------------------")

# increments the value to increment, deletes the duplicate entries, sorts the DNS entries, reconstructs the file and replaces the old file with the new one
for file in DNS_files:
    logger.info(f"incrementing the value for {file.name} ...")
    file.increment_incre_value()
    logger.info(f"deleting the duplicate entries for {file.name} ...")
    file.delete_duplicate_entries()
    logger.info(f"sorting the DNS entries for {file.name} ...")
    file.sort_DNS_entries()
    logger.info(f"reconstructing the file {file.name} ...")
    file.reconstruct_file()
    logger.info(f"replacing the old file with the new one for {file.name} ...")
    #file.replace_file()
    logger.info(f"-----------------------------")
    
    
logger.info("The program has finished running.")

# Should I add Docstrings ?


#///
#