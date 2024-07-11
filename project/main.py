import logging
import sys
from pathlib import Path
from project.argumentparser.ArgumentParser import ArgumentParser
from project.files.DNSFile import DNSFile
from project.logger.CustomFormatter import CustomFormatter
import os

# Setup the directory that contains main.py as the working directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

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
    if args.files == None:
        logger.error("No files were passed as arguments. Please pass the files you want to sort.")
        # print the help message
        arg_parser.parser.print_help()
        sys.exit(1)
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
