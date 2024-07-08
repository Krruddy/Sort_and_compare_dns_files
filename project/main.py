import logging
from pathlib import Path
from project.argumentparser.ArgumentParser import ArgumentParser
from project.files.DNSFile import DNSFile
from project.logger.CustomFormatter import CustomFormatter
from project.operation.Sorter import Sorter

"""
This program increments the number on line 3, removes the duplicates and sorts based on IP addresses the DNS entries. 
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
# TODO create an abstract class for LOOMFile and DNSFile

# Create a logger
logger = logging.getLogger("my_logger")

# Create a StreamHandler and set the custom formatter
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())

# Add the handler to the logger
logger.addHandler(handler)

# Set the logging level
logger.setLevel(logging.INFO)

if __name__ == "__main__":

    ## Initialize the path to the DNS files and to the LOOM directory
    arg_parser = ArgumentParser()
    args = arg_parser.parse_arguments()
    files = [Path(file) for file in args.files] # TODO exception if no arguments are passed

    #sorter = Sorter(files)
    #sorter.sort()

    dns_files = {}
    for file in files:
        if file.is_file():
            dns_files[file.name] = DNSFile(file)

    for dns_file in dns_files.values():
        dns_file.sort()
        dns_file.save()