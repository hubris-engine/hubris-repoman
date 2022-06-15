from argparse import ArgumentParser
from pathlib import Path

import hubris
import hubris.filesystem as fs
import hubris.algorithm as algo

parser = ArgumentParser(description="Replaces the shebang in a shell script")
parser.add_argument("path", type=Path, help="Path to the shell script file")
parser.add_argument("shebang", type=str, help="What to replace the shebang with")
parser.add_argument("--recursive", action="store_true", help="Recursively looks for shell script (.sh) files")

args = parser.parse_args()
file_path = Path(args.path).resolve(strict=True)

shebang : str = args.shebang

# Idiot proof shebang
shebang = shebang.strip()
if not shebang.startswith("!"):
    shebang = "!" + shebang


def replace_shebang(file_path : Path, shebang : str):

    # Read in file
    file_str : str = ""
    with open(file_path, "r") as file:
        file_str = file.read()

    if not file_str.startswith("#"):
        hubris.log_error(f"No shebang to replace in file at path {str(file_path)}")
        exit(1)

    # Find end of first line
    eol_pos = file_str.find('\n')
    if eol_pos == -1:
        eol_pos = len(file_str)
    elif eol_pos != len(file_str):
        eol_pos = eol_pos + 1

    # Remove first line
    file_str = file_str[eol_pos:]

    # Insert new shebang to top of file
    file_str = f"#{shebang}\n" + file_str

    # Write to disk
    with open(file_path, "w") as file:
        file.write(file_str)


paths : "list[Path]" = []
if args.recursive:
    
    # Find shell script paths (recursive)
    paths : "list[Path]" = algo.transform(
            fs.filter_children(
                file_path,
                lambda x : x.suffix == ".sh",
                recursive=True),
            lambda x : str(x))

else:
    paths = [str(file_path)]


for v in paths:
    replace_shebang(v, shebang)

