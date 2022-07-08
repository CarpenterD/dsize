import os
from sys import stderr
import argparse


# Helper Functions ------------------------------------------------------------
def formattedSize(num, suffix="B", binary=True):
    base = 1024.0 if binary else 1000.0
    if binary:
        units = ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]
    else:
        units = ["", "k", "M", "G", "T", "P", "E", "Z"]

    for unit in units:
        if abs(num) < base:
            return f"{num:3.1f} {unit}{suffix}"
        num /= base
    return f"{num:.1f}Y{suffix}"

# Class, Parser and Printing --------------------------------------------------
class Directory:
    def __init__(self, path:str):
        self.path:str = path
        self.name:str = os.path.basename(path)
        self.size:int = 0
        self.fileCount:int = 0
        self.filesSize:int = 0 # total size of files (excluding directories)
        self.childDirectories:list[Directory] = []
        self.parent = None

    def addFileSize(self, size:int):
        self.fileCount += 1
        self.filesSize += size
        self.size += size

    def addChild(self, directory):
        self.childDirectories.append(directory)
        directory.parent = self
        self.size += directory.size


def parseDirectory(path:str, maxDepth:int = -1) -> Directory:
    directory = Directory(path)
    with os.scandir(path) as dirScan:
        for item in dirScan:
            if item.is_dir(follow_symlinks=False) and (maxDepth > 0 or maxDepth == -1):
                child = parseDirectory(item.path, (maxDepth-1) if maxDepth > 0 else -1)
                directory.addChild(child)
            elif item.is_file(follow_symlinks=False):
                stats = os.lstat(item.path)
                directory.addFileSize(stats.st_size)
            else:
                pass # symbolic links etc.
    return directory

def printDirectory(directory:Directory, totalSize, depth:int=0, binaryUnits:bool=False, maxDepth:int=-1):
    totalFrac = directory.size/totalSize
    print("    " * depth, "-", "{:>5.1%}".format(totalFrac), f"({formattedSize(directory.size, binary=binaryUnits)})", "\t", directory.name)
    for child in sorted(directory.childDirectories, key=lambda d: d.size, reverse=True):
        if depth < maxDepth:
            printDirectory(child, totalSize, depth=depth+1, binaryUnits = binaryUnits, maxDepth=maxDepth)
    if directory.fileCount > 0 and depth < maxDepth:
        filesFraction = 0 if directory.size == 0 else directory.filesSize/totalSize
        print(("    " * (depth+1)), "-", "{:>5.1%}".format(filesFraction), f"({formattedSize(directory.filesSize, binary=binaryUnits)})", "\t", f"Other files ({directory.fileCount} total)")
            
# Main function ---------------------------------------------------------------
def configureParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", nargs="?", default=os.getcwd(),
            help="target directory; defaults to the current working directory")
    parser.add_argument("-d", "--output-depth", type=int, default=1,
            help="recursive output depth; or -1 for no limit")
    parser.add_argument("-b", "--binary", action="store_true", 
            help="output sizes in binary units")
    return parser

def main():
    parser = configureParser()
    args = parser.parse_args()

    path = args.dir
    if not os.path.exists(path):
        print(f"\"{path}\" was not found", file=stderr)
        exit(1) 
    if not os.path.isdir(path):
        print(f"\"{path}\" is not a directory", file=stderr)
        exit(1) 

    directory = parseDirectory(path)
    printDirectory(directory, directory.size, binaryUnits=args.binary, maxDepth=args.output_depth)

if __name__ == "__main__":
    main()