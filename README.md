# DNS Sorting and Comparison Tool

This project contains a Python script (`dns_sorting.py`) that compares DNS files with LOOM files, sorts DNS entries, and performs other related tasks.

This project uses "dns...." from the dnspython library to parse DNS files.

## Project Structure

```bash
.vscode/ settings.json LOOM/ README.md main.py notes.md dns_backups/ 10.10.db.dns_backups ruddy.db.dns_backups
```
## Installation

Before running the script, make sure you have Python installed on your machine. If your project has other dependencies, list them here along with instructions on how to install them.

## Features

- **DNS_file class**: This class represents a DNS file. It provides methods for finding the file type, setting file content, finding and incrementing values, deleting duplicate entries, sorting DNS entries, and reconstructing the file.

- **LOOM_file class**: This class represents a LOOM file. It provides methods for setting file content.

- **Comments class**: This class represents comments in a DNS file. It provides methods for adding, removing, and displaying comments.

## Usage

To use the script, you need to have Python installed on your machine. Run the script with the desired DNS file as an argument.

```bash
python main.py <filename>
```

Replace <filename> with the actual filename you want to use.

## Contributing
Contributions are welcome. Please fork the repository and create a pull request with your changes.

## License
This project is not licensed licensed.
