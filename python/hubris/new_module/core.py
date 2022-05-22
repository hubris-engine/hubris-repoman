

import re
import os

import hubris
import hubris.filesystem as fs



_INVALID_MODULE_NAME_REGEX = re.compile("[^a-zA-Z_\-]")







class ModuleInfo:

	def __init__(self, name : str, root : fs.Path):
		self.name = name
		self.root = root



def make_cmakelists(module : ModuleInfo):
	path = module.root.joinpath("CMakeLists.txt")

	_CMAKE_MINIMUM_VERSION = "3.12"
	_CMAKE_PROJECT_NAME = module.name
	_CMAKE_LIBRARY_NAME = "${PROJECT_NAME}"
	_CMAKE_LIBRARY_TYPE = "STATIC"
	_CMAKE_LIBRARY_SOURCES = [
		f"source/{module.name}.cpp"
	]
	_CMAKE_LIBRARY_INCLUDE_PUBLIC = [
		f"include"
	]
	_CMAKE_LIBRARY_INCLUDE_PRIVATE = [
		f"source"
	]

	_CMAKE_LIBRARY_INSTALL_DESTINATION = f"lib/"

	_CMAKE_VAR_INCLUDE_PUBLIC  = "_include_public"
	_CMAKE_VAR_INCLUDE_PRIVATE = "_include_private"
	
	_CMAKE_VAR_LINK_PUBLIC  = "_link_public"
	_CMAKE_VAR_LINK_PRIVATE = "_link_private"

	_CMAKE_VAR_SOURCES = "_sources"


	_TABBED_NEWLINE = "\n\t"

	_LINES = [
		f"cmake_minimum_required(VERSION {_CMAKE_MINIMUM_VERSION})",
		 "",
		f"""project({_CMAKE_PROJECT_NAME}
	VERSION 0.1)""",
		 "",
		 "# The library's sources",
		f"""set({_CMAKE_VAR_SOURCES} 
	{_TABBED_NEWLINE.join(_CMAKE_LIBRARY_SOURCES)})""",
		"",
		 "# The library's public linked libraries",
		f"""set({_CMAKE_VAR_LINK_PUBLIC} 
	)""",
		"",
		 "# The library's private linked libraries",
		f"""set({_CMAKE_VAR_LINK_PRIVATE}
	)""",
		 "",
		 "# The library's public include directories",
		f"""set({_CMAKE_VAR_INCLUDE_PUBLIC}
	{_TABBED_NEWLINE.join(_CMAKE_LIBRARY_INCLUDE_PUBLIC)})""",
		"",
		 "# The library's private include directories",
		f"""set({_CMAKE_VAR_INCLUDE_PRIVATE}
	{_TABBED_NEWLINE.join(_CMAKE_LIBRARY_INCLUDE_PRIVATE)})""",
		"",
		"",
		"###",
		"###  INTERNAL",
		"###",
		"",
		f"add_library({_CMAKE_LIBRARY_NAME} {_CMAKE_LIBRARY_TYPE} ${{{_CMAKE_VAR_SOURCES}}})",
		"",
		f"""target_include_directories({_CMAKE_LIBRARY_NAME}
	PUBLIC ${{{_CMAKE_VAR_INCLUDE_PUBLIC}}}
	PRIVATE ${{{_CMAKE_VAR_INCLUDE_PRIVATE}}})""",
		"",
		f"""target_link_libraries({_CMAKE_LIBRARY_NAME}
	PUBLIC ${{{_CMAKE_VAR_LINK_PUBLIC}}}
	PRIVATE ${{{_CMAKE_VAR_LINK_PRIVATE}}})""",
		"",
		"# Trickle down",
		"ADD_CMAKE_SUBDIRS_HERE()",
		"",
		f"install(TARGETS {_CMAKE_LIBRARY_NAME} DESTINATION {_CMAKE_LIBRARY_INSTALL_DESTINATION})",
		"",
	]

	with open(path, "w") as file:
		for v in _LINES:
			file.write(v + '\n')

	return

def make_gitignore(module : ModuleInfo):
	path = module.root.joinpath(".gitignore")
	
	_LINES = [
		"# IDE",
		".vs/",
		".vscode/",
		"CMakeSettings.json",
		"",
		"# Output directories",
		"out/",
		"",
		"# Generic",
		"_*/",
	]

	with open(path, "w") as file:
		for v in _LINES:
			file.write(v + '\n')
	return

def make_readme(module : ModuleInfo):
	path = module.root.joinpath("readme.txt")

	with open(path, "w") as file:
		file.write(f"{module.name} module\n")

	return

def make_include(module : ModuleInfo):
	path = module.root.joinpath("include")
	os.mkdir(path)

	os.mkdir(path.joinpath(module.name))
	
	with open(path.joinpath(module.name, module.name + ".hpp"), "w") as file:
		file.write("#pragma once\n\n/** @file */\n\nnamespace hubris\n{\n\t\n\t\n\t\n};\n")

	return

def make_source(module : ModuleInfo):
	path = module.root.joinpath("source")
	os.mkdir(path)

	with open(path.joinpath(module.name + ".cpp"), "w") as file:
		file.write(f"#include <{module.name}/{module.name}.hpp>\n\n\n\nnamespace hubris\n")
		file.write("{\n\t\n\t\n\t\n};\n")

	return


_FILE_TEMPLATES = [
	make_cmakelists,
	make_gitignore,
	make_readme,
	make_include,
	make_source,
]




def new_module(name : str,
	output_root : "fs.Path | None" = None):

	# Validate the name
	match = _INVALID_MODULE_NAME_REGEX.match(name)
	if match:
		# Name contained invalid characters
		hubris.log_error(f"Invalid module name {name}")
		return 1

	# Handle the output root path variable
	output_root =  fs.Path(output_root or fs.Path.cwd().joinpath(name)).absolute()
	
	# Check the output root
	if output_root.exists():
		if output_root.is_dir():
			if not fs.is_empty(output_root):
				hubris.log_error(f"Output directory {str(output_root)} exists and isn't empty")
				return 1
		else:
			hubris.log_error(f"Output path {str(output_root)} exists and isn't an empty directory")
			return 1
	else:
		os.makedirs(output_root)


	# Create the contents
	m = ModuleInfo(name, output_root)
	for v in _FILE_TEMPLATES:
		v(m)



