# DNS Sorting and Comparison Tool

This project is a Python script that reads a DNS file, sorts the entries, and removes duplicates.

It uses the following libraries:

- os
- sys
- ...

## Installation

Before running the script, make sure you have Python installed on your machine. You will find the libraries used in the script in the requirements.txt file and the libraries themselves in libraries. You can install them using `pip install libraries/*`.

In order to setup the project module, you can run the following command in the root directory of the project (where `project` is reachable):

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/project"
```

## Usage

To use the script, you need to have Python installed on your machine. Run the script with the desired DNS file as an argument.

```bash
python main.py <filename>
```