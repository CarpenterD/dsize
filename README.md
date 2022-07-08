# dsize
Calculates the size of a directory and all of its children.

The intention of this tool is to help isolate large nested directories without having to manually explore their children.

## Usage
Calculate the size of the current directory:
```shell
python dsize
```

Calculate the size of a different directory and display results using binary units (KiB, MiB etc.):
```shell
python dsize path\to\directory --binary
```

Display usage information and available options:
```shell
python dsize --help
```