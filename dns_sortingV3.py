import re
import ipaddress
import os
import sys
import logging
import errno
import filecmp  

manual_LOOM_path = "/home/ruddy/Documents/LOOM"

"""
 This program increments the number of line 3, removes the duplicates and sorts based on IP addresses the DNS entries. 
 This program does not delete the old file, it renames it with the extension ".old" and creates a new file with the same name as the old one.
 For the program to work, the following conditions must be met:
 - The file must only contain A records (the other records will be ignored).
 - The number that has to be incremented must be in the third line of the file.
 - The only ip addresses present in the standard DNS file must be part of the DNS entries. 
 - The only ip addresses (with the patern "XXX.XXX") present in the reverse DNS must be part of the DNS entries.
 - The name of the reverse DNS file must look like this "XXX.XXX.db" otherwise the program will consider it as a standard DNS file.
 The second part of this program is going to compare the DNS file provided with the DNS file present in the "LOOM" directory.
 For this part of the program to work, the following conditions must be met:
 - nothing different from the conditions above.
 - If possible no comments in the DNS files.
"""

# raised when the entries in the DNS file and the LOOM file are identical
class IdenticalEntries(Exception):  
    pass

class NoChangesMade(Exception):
    pass

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
        self.type = self.__find_file_type(self.name)
        self.file_content = self.__set_file_content(self.name)
        self.space_before_incre_value = self.__find_space_before_incre_value(self.file_content[2])
        self.incre_value = self.__find_incre_value(self.file_content[2])
        self.list_of_DNS_entries = self.__set_list_of_DNS_entries(self.file_content)
        self.comments = self.__set_comments(self.file_content)

    # a function named __find_file_type that takes the name of the file and returns the type of file (standard DNS or reverse DNS)      
    def __find_file_type(self, name_of_file: str, rev_pattern = r"\d{1,3}\.db$"):
        if re.search(rev_pattern, name_of_file) == None:
            return "standard DNS"
        else:
            return "reverse DNS"
        
    # a function named __set_file_content that takes the name of the file and returns the content of the file in a list
    def __set_file_content(self, name_of_file: str):
        file = open(f"{name_of_file}", "r")
        lines = file.readlines()
        file.close()
        return lines
    
    # a functionn named __find_space_before_incre_value that takes the line containing the value to increment and returns the amount of spaces before the value to increment
    def __find_space_before_incre_value(self, incre_value_line: str):
        amount_of_spaces = incre_value_line.count(' ') - 1
        return amount_of_spaces
        
    # a function named __find_incre_value that takes the line containing the value to increment and returns the value to increment
    def __find_incre_value(self, incre_value_line: str):
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

    # a function named __set_list_of_DNS_entries that takes self, the file content and returns a list of DNS entries
    def __set_list_of_DNS_entries(self, file_content: list):
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

    def __set_comments(self, file_content: list):
        return 0
   
    # a function named increment_incre_value that increments the value to increment
    def increment_incre_value(self):
        self.incre_value += 1
    
    # a function named delete_duplicate_entries that deletes the duplicate entries
    def delete_duplicate_entries(self, LOOM = False):
        if LOOM and not self.identical_to_LOOM:
            if self.LOOM_list_of_DNS_entries == list(set(self.LOOM_list_of_DNS_entries)):
                logger.info(f"LOOM does not contain any duplicate entries.")
            else:
                logger.warning(f"The LOOM file of {self.name} contains duplicate entries.")
                logger.warning(f"Deleting locally the duplicate entries (the actual LOOM file will remain unchanged) ...")
                self.LOOM_list_of_DNS_entries = list(set(self.LOOM_list_of_DNS_entries))
        if not LOOM:
            self.list_of_DNS_entries = list(set(self.list_of_DNS_entries))

    def sort_DNS_entries(self, LOOM = False):

        if LOOM and not self.identical_to_LOOM:
            if self.type == "standard DNS":
                self.sort_standard_DNS_entries(LOOM)
            else:
                self.sort_reverse_DNS_entries(LOOM)
        if not LOOM:
            if self.type == "standard DNS":
                self.sort_standard_DNS_entries(LOOM)
            else:
                self.sort_reverse_DNS_entries(LOOM)

    # a function named sort_standard_DNS_entries that sorts the standard DNS entries
    def sort_standard_DNS_entries(self, LOOM: bool):
        if LOOM:
            list_of_DNS_entries = self.LOOM_list_of_DNS_entries
        if not LOOM:
            list_of_DNS_entries = self.list_of_DNS_entries


        list_of_ip = [re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", line) for line in list_of_DNS_entries]
        list_of_ip = [item for sublist in list_of_ip for item in sublist] 
        sorted_list_of_ip = sorted(list_of_ip, key = ipaddress.IPv4Address)
        sorted_DNS_entries = []
        for ip in sorted_list_of_ip:
            for DNS_entry in list_of_DNS_entries:
                if ip in DNS_entry:
                    sorted_DNS_entries += [DNS_entry]
        print(sorted_DNS_entries)
        if LOOM:
            if sorted_DNS_entries == self.LOOM_list_of_DNS_entries:
                logger.info(f"LOOM was already sorted.")
            else:
                logger.warning(f"LOOM was not sorted, but now locally is (the actual LOOM file will remain unchanged).")
                self.LOOM_list_of_DNS_entries = sorted_DNS_entries

        if not LOOM:
            self.list_of_DNS_entries = sorted_DNS_entries
            
     
    # a function named sort_reverse_DNS_entries that sorts the reverse DNS entries   
    def sort_reverse_DNS_entries(self, LOOM: bool):
        if LOOM:
            list_of_DNS_entries = self.LOOM_list_of_DNS_entries
        if not LOOM:
            list_of_DNS_entries = self.list_of_DNS_entries
        
        list_of_ip = [re.findall(r"\d{1,3}\.\d{1,3}", line) for line in list_of_DNS_entries]
        list_of_ip = [item for sublist in list_of_ip for item in sublist] # list of ip is a list of lists, this line flattens the list
        sorted_list_of_ip = sorted(list_of_ip, key=lambda ip: [int(octet) for octet in ip.split('.')])
        
        sorted_DNS_entries = []
        for ip in sorted_list_of_ip:
            for DNS_entry in list_of_DNS_entries:
                if ip in DNS_entry:
                    sorted_DNS_entries += [DNS_entry]
        
        if LOOM:
            self.LOOM_list_of_DNS_entries = sorted_DNS_entries
        if not LOOM:
            self.list_of_DNS_entries = sorted_DNS_entries

    # a function named reconstruct_file that reconstructs the file with the new incrementation value and the sorted DNS entries
    def reconstruct_file(self, LOOM = False):
        # Reconstructs the 2nd line
        reconstructed_line = self.__reconstruct_line(self.space_before_incre_value, self.incre_value)
        
        # Open the file
        if LOOM:
            final_DNS_file = self.__create_tmp_file(f"{self.name}._after_LOOM")
        if not LOOM:
            final_DNS_file = self.__create_tmp_file(f"{self.name}")
        
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
    
    def __create_tmp_file(self, name: str):
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
    def __reconstruct_line(self, amount_of_spaces: int, incremented_value: int):
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

    def setup_LOOM_config(self, LOOM_path = None):
        self.LOOM_file_path = self.__find_LOOM_file_path(self.name, LOOM_path)
        self.LOOM_file_exists = self.__LOOM_file_exists_and_set(self.LOOM_file_path)
        
        if self.LOOM_file_exists: 
            if not self.fast_comp(self.LOOM_file_path):
                self.identical_to_LOOM = False    
                self.LOOM_file_content = self.set_LOOM_file_content(self.LOOM_file_path)
                self.LOOM_list_of_DNS_entries = self.__set_list_of_DNS_entries(self.LOOM_file_content)
            else:
                self.identical_to_LOOM = True
                self.LOOM_file_content = None
                self.LOOM_list_of_DNS_entries = None
                logger.info(f"The file {self.name} is the same as the LOOM file {self.LOOM_file_path}.")

                
        else:
            raise FileNotFoundError

    def __find_LOOM_file_path(self, name: str, LOOM_path):
            return f"{LOOM_path}/{name}"

    def __LOOM_file_exists_and_set(self, LOOM_file_path: str):
        if os.path.isfile(LOOM_file_path) == False:
            logger.warning(f"The LOOM file {LOOM_file_path} does not exist.")
            logger.warning(f"The comparison between {self.name} and {LOOM_file_path} will not take place.")
            return False
        else:
            return os.path.isfile(LOOM_file_path)

    # a function named set_LOOM_file_content that takes the path to the LOOM file and returns wether or not the DNS file and the LOOM file are the same.
    def fast_comp(self, LOOM_file_path: str):
        return filecmp.cmp(self.name, LOOM_file_path, shallow=False)
    
    def set_LOOM_file_content(self, LOOM_file_path: str):
        if os.path.isfile(LOOM_file_path):
            file = open(f"{LOOM_file_path}", "r")
            lines = file.readlines()
            file.close()
            return lines
        else:
            logger.warning(f"The LOOM file {LOOM_file_path} does not exist.")
            return None
    
    def fast_comp(self, LOOM_path: str):
        if LOOM_path == None:
            return False
   
    def compare_DNS_entries(self):
        if not self.identical_to_LOOM:
            if self.type == "standard DNS":
                index_of_ip = 3
                index_of_server_name = 0
                ip_in_ip_in_DNS = index_of_server_name
            else:
                index_of_ip = 0
                index_of_server_name = 3
                ip_in_ip_in_DNS = 0
                
            Tokenized_DNS_entries = [line.split() for line in self.list_of_DNS_entries]
            Tokenized_LOOM_DNS_entries = [line.split() for line in self.LOOM_list_of_DNS_entries]
                        
            
            # Entries that are in the LOOM file but not in the DNS file
            line_not_in_DNS = [line for line in Tokenized_LOOM_DNS_entries if line not in Tokenized_DNS_entries]
            # ip addresses (and name server on LOOM) that are in the LOOM file and in the DNS file but don't point to the same server
            # the key is the ip address and the value is the name of the server that corresponds to the ip address in the LOOM file
            #ip_in_DNS = [[line[index_of_ip],line[index_of_server_name]] for line in line_not_in_DNS if line[index_of_ip] in [line[index_of_ip] for line in Tokenized_DNS_entries]]
            ip_in_DNS = {line[index_of_ip]:line[index_of_server_name] for line in line_not_in_DNS if line[index_of_ip] in [line[index_of_ip] for line in Tokenized_DNS_entries]}
            
            # name of the server that corresponds to the ip address in the LOOM file (the name server that has a different ip address in the DNS file from the LOOM file)
            server_names_of_ip_in_DNS = [line[index_of_server_name] for line in Tokenized_DNS_entries if line[index_of_ip] in list(ip_in_DNS.keys())]
            
            
            # If the LOOM file does not contain any entries that are not in the DNS file, then there is no need to ask the user for changes.
            if len(line_not_in_DNS) == 0:
                logger.info(f"The LOOM file {self.LOOM_file_path} does not contain any entries that are not in the DNS file {self.name}.")
                raise IdenticalEntries
            
            # If the user does not approve any changes, then there is no need to continue the treatment of this file.
            changes_manually_approved = False
            
            # Ask the user if the lines present in the LOOM file but not in the DNS file should be added to the DNS file.
            for line in line_not_in_DNS:
                if line[index_of_ip] not in list(ip_in_DNS.keys()):
                    print(f"\n\n", "-" * 80)
                    print(f"The DNS entry that makes the ip address {line[index_of_ip]} point to the server {line[index_of_server_name]} is present in the LOOM file {self.LOOM_file_path} but not in the local DNS file {self.name}.")
                    print("See the entry below. \n")
                    print(f"{' '.join(line)}\n")
                    
                    for attempt in range(3):
                        answer = input(f"Would you like to add that entry to the local DNS file {self.name} ? (y/N) : ")
                        if answer.lower() == "y":
                            logger.info(f"Adding the entry {' '.join(line)} to the local DNS file {self.name} ...")
                            self.list_of_DNS_entries += [' '.join(line) + '\n']
                            changes_manually_approved = True
                            break
                        elif answer.lower() == "n" or answer == "":
                            logger.info(f"The entry {' '.join(line)} will not be added to the local DNS file {self.name}.")
                            break
                        else:
                            print(f"invalide answer, please try again.")
                        
            
            # Ask the user if the lines that contain an ip address that is present in both files but points to a different server should be changed to what is present in the LOOM file.
            #for index, ip in enumerate(ip_in_DNS):
            for index, (ip, server_name_in_LOOM) in enumerate(ip_in_DNS.items()):
                print(f"\n\n", "-" * 80)
                print(f"In the LOOM file, the ip address {ip} points to the server {server_name_in_LOOM}. Meanwhile in the DNS file, it points to the server {server_names_of_ip_in_DNS[index]}.")
                print(f"In the LOOM file, the entry is")
                print(f"{' '.join(Tokenized_DNS_entries[[line[index_of_ip] for line in Tokenized_DNS_entries].index(ip)])}\n") # I don't understand this line and I don't want to try to understand it. thx copilot
                print(f"In the DNS file, the entry is")
                print(f"{' '.join(Tokenized_LOOM_DNS_entries[[line[index_of_ip] for line in Tokenized_LOOM_DNS_entries].index(ip)])}\n")
                
                for attempt in range(3):
                    answer = input(("would you like to change the entry in the DNS file to what is present in the LOOM file ? (y/N) : "))
                    if answer.lower() == "y":
                        logger.info(f"Changing the entry {' '.join(Tokenized_LOOM_DNS_entries[[line[index_of_ip] for line in Tokenized_LOOM_DNS_entries].index(ip)])} to {' '.join(Tokenized_DNS_entries[[line[index_of_ip] for line in Tokenized_DNS_entries].index(ip)])} ...") # again, I don't know what this is.
                        self.list_of_DNS_entries[[line[index_of_ip] for line in Tokenized_DNS_entries].index(ip)] = ' '.join(Tokenized_LOOM_DNS_entries[[line[index_of_ip] for line in Tokenized_LOOM_DNS_entries].index(ip)]) + '\n' #???????????????
                        changes_manually_approved = True
                        break    
                    elif answer.lower() in ["n", ""]:
                        logger.info(f"The entry {' '.join(Tokenized_LOOM_DNS_entries[[line[index_of_ip] for line in Tokenized_LOOM_DNS_entries].index(ip)])} will not be changed.")
                        break
                    else:
                        print(f"invalide answer, please try again.")
            if not changes_manually_approved:
                logger.info(f"No changes have been made to the local DNS file {self.name}.")
                raise NoChangesMade      
                                
    def establish_LOOM_differences(self):
        self.LOOM_differences = {
                    "incrementation value": False,
                    "sorted": False,
                    "duplicate entries": False,
                    "DNS entries": False
                }
        
    def beautify_DNS_entries(self):
        Tokenized_DNS_entries = [line.split() for line in self.list_of_DNS_entries]
        longest_server_name = max([len(line[0]) for line in Tokenized_DNS_entries])
        
        for line in Tokenized_DNS_entries:
            added_spaces = longest_server_name - len(line[0])
            line[0] += " " * added_spaces
            line[1] += " " * 6
            line[2] += " " * 7        

        self.list_of_DNS_entries = [' '.join(line) + '\n' for line in Tokenized_DNS_entries] 
        
def parse_arguments():
    logger.info("Parsing the arguments ...")
    if len(sys.argv) == 1:
        logger.error(f"No arguments have been passed.")
        logger.error(f"Exiting the program.")
        sys.exit(errno.ENOENT)
    else:
        if "--help" in sys.argv or "-h" in sys.argv:
            print(f"Here are an examples of how to use this program :\n")
            print(f"python3 dns_sorting.py dnsfile.db \n")
            print(f"python3 dns_sorting.py dnsfile.db 10.10.db\n")
            print(f"python3 dns_sorting.py --LOOM_path /home/ruddy/Documents/LOOM/ dnsfile.db 10.10.db\n")
            print("-" * 80)
            print("exiting the program ...")
            sys.exit(0)
        elif "--LOOM_path" in sys.argv:
            if len(sys.argv) <= 3:
                logger.error(f"No file has been passed as an argument.")
                logger.error(f"Exiting the program.")
                sys.exit(errno.ENOENT)
            else:    
                LOOM_path = sys.argv[sys.argv.index("--LOOM_path") + 1]
                logger.info(f"The path to the LOOM directory is {LOOM_path}.")
        else:
            LOOM_path = None
            logger.warning(f"The path to the LOOM directory is not specified, using the path predefined in the program.")
            
        # populates the list of DNS_files
        DNS_files = []
        logger.info(f"Populating the DNS list ...")
        for index, argument in enumerate(sys.argv):
            if argument == "--LOOM_path" or sys.argv[index - 1] == "--LOOM_path":
                continue
            elif index != 0:
                logger.info(f"adding {argument} to the list of DNS files ...")
                DNS_files += [DNS_file(argument)]
                print(f"-" * 80)
        
        return DNS_files, LOOM_path
    
logger.info("Starting the program.")

DNS_files, LOOM_path = parse_arguments()

if LOOM_path == None:
    LOOM_path = manual_LOOM_path
                        
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
    print(f"-" * 80)
    
###################################
# The file comparison starts here #
###################################

print(f"\n" * 2)
print(f"#" * 32)
print(f"# Starting the file comparison #")
print(f"#" * 32, "\n\n")
print(f"\n" * 2)

#define the path to the LOOM directory and check if it exists
if os.path.isdir(f"{LOOM_path}") == False:
    logger.error(f"The path {LOOM_path} is not valid.")
    logger.error(f"The comparison between the DNS files and the LOOM files cannot be done.")
    logger.error(f"Exiting the program.")
    sys.exit(errno.ENOENT)

for file in DNS_files:
    try:
        logger.info(f"Setting up the LOOM configuration for {file.name} ...")
        file.setup_LOOM_config(LOOM_path)
    except FileNotFoundError:
        print(f"-" * 80)
        continue
    logger.info(f"Looking for duplicates in the LOOM file {file.LOOM_file_path} ...")
    file.delete_duplicate_entries(LOOM = True)
    # It's useless to sort the content of the variable that contains the LOOM file content because it's not going to be written to the file.
    #logger.info(f"Attempting to sort the LOOM file {file.LOOM_file_path} ...")
    #file.sort_DNS_entries(LOOM = True)
    try:
        logger.info(f"Comparing the DNS entries of the file {file.name} with the LOOM file {file.LOOM_file_path} ...")
        file.compare_DNS_entries()
    except (IdenticalEntries, NoChangesMade):
        print(f"-" * 80)
        continue
    file.sort_DNS_entries(LOOM = True)
    logger.info(f"reconstructing the file {file.name} with the added entries to the DNS file ...") 
    file.beautify_DNS_entries()
    file.reconstruct_file(LOOM = True)
    logger.info(f"replacing the old file with the new one for {file.name} ...")
    #file.replace_file()
    print(f"-" * 80)

logger.info("The program has finished running.")

# Open an apache2 web server on port 80


# Should I add Docstrings ?
# Add a function that checks if all of the DNS entries are of type A (read the 3rd word of the lines that contain an ip address).
# Have None instead of having objects with missing attributes.
# Sort and delete duplicates in the object that represents the LOOM file, but don't write it to the file.
# if there are duplicates in LOOM warn the user.
# After having asked for the changes to the user, do a last check between the DNS file and the LOOM file. then if they aren't the same warn the user.
#have an __str__ method for the DNS_file class.
# hanfdle comments in the DNS files dictionary key=line, value=comment
"""
Crtl + Alt + f send to suspicious (en piece jointe)
C1 à C3, C4 est confidentiel
mail C1 à C3
AGI 
"""
