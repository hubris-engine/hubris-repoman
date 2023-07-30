# Enables ADD_GIT_DEPENDENCY functionality
option(ENABLE_GIT_DEPENDENCIES "Enables automatic cloning of dependencies that do not already exit" ON)


find_package(Git QUIET)




#
#	Adds a new dependency and automatically clones it if the target does not already exist.
#
#	@param depPath Where to clone the repo into, must be an absolute path!
#	@param depTarget Name of the target, this is used to check if the dependency already exists
#	@param depRepo Path or URL to clone the repo from
#	@param branchName? Name of the branch to clone, defaults to HEAD
#
function(ADD_GIT_DEPENDENCY_FN depPath depTarget depRepo)

	# Ignore if target already exists
	if (NOT TARGET ${depTarget})
	 
		# Add the subdir if it already exists and has a CMake support
		if (EXISTS "${depPath}/CMakeLists.txt")
			add_subdirectory("${depPath}")
			
			# Check that dependency target is now defined
			if (NOT TARGET ${depTarget})
				message(FATAL "Cloned dependency has a CMakeLists but the dependency target was not defined!")
			endif()
			
		else()

			# Only preform branch if git dependencies are allowed
			if (ENABLE_GIT_DEPENDENCIES)
		
				set(gitResult )

				# Use branch optional parameter if it was provided
				if (ARGC GREATER 3)
					execute_process(COMMAND
						${GIT_EXECUTABLE} clone -b "${ARGV3}" ${depRepo} ${depPath}
						RESULTS_VARIABLE gitResult)
				else()
					execute_process(COMMAND
						${GIT_EXECUTABLE} clone ${depRepo} ${depPath}
						RESULTS_VARIABLE gitResult)
				endif()

				# Add the cloned repo as a subdir if it has CMake support
				if (EXISTS "${depPath}/CMakeLists.txt")
					add_subdirectory("${depPath}")
			
					# Check that dependency target is now defined
					if (NOT TARGET ${depTarget})
						message(FATAL "Cloned dependency has a CMakeLists but the dependency target was not defined!")
					endif()
				
				endif()
			
			endif()

		endif()

	endif()
endfunction()

#
#	Adds a new dependency and automatically clones it if the target does not already exist.
#
#	@param depPath Relative path to clone the repo into
#	@param depTarget Name of the target, this is used to check if the dependency already exists
#	@param depRepo Path or URL to clone the repo from
#	@param branchName? Name of the branch to clone, defaults to HEAD
#
macro(ADD_GIT_DEPENDENCY depPath depTarget depRepo)

	# Make file path absolute
	set(__addgitdepedency_realpath ${depPath})
	#file(REAL_PATH ${depPath} __addgitdepedency_realpath)
	
	# Determine invocation syntax
	if (${ARGC} GREATER 3)
		# Invoke with branchName parameter
		ADD_GIT_DEPENDENCY_FN(${__addgitdepedency_realpath} ${depTarget} ${depRepo} ${ARGV3})
	else()
		# Invoke without branchName parameter
		ADD_GIT_DEPENDENCY_FN(${__addgitdepedency_realpath} ${depTarget} ${depRepo})
	endif()
endmacro()


#
#	Adds a list of sources to a target, sourceList should be a list variable
#
macro(ADD_SOURCES_LIST targetName sourceList)
	list(TRANSFORM ${sourceList} PREPEND "${CMAKE_CURRENT_SOURCE_DIR}/")
	set(lfefiles )
	foreach(lfe IN LISTS ${sourceList})
		set(lfefiles ${lfefiles} ${lfe})
	endforeach()
	target_sources(${targetName} PRIVATE ${lfefiles})
endmacro(ADD_SOURCES_LIST)

#
#	Returns the child DIRECTORY paths of a given directory
#
macro(SUBDIRLIST result curdir)
	file(GLOB children RELATIVE ${curdir} ${curdir}/*)
	set(dirlist "")
	foreach(child ${children})
		if(IS_DIRECTORY ${curdir}/${child})
			list(APPEND dirlist ${child})
		endif()
	endforeach()
	set(${result} ${dirlist})
endmacro()

macro(SUBDIRLIST_RECURSIVE out_Dirs in_Path)
	set(__curDirs )
	SUBDIRLIST(__curDirs ${in_Path})
	list(TRANSFORM __curDirs PREPEND "${in_Path}/")
	list(APPEND ${out_Dirs} ${__curDirs})
	foreach(lfe IN LISTS __curDirs)
		SUBDIRLIST_RECURSIVE(${out_Dirs} ${lfe})
	endforeach()
endmacro()

#
#	Returns the child paths of a given directory
#
macro(GET_DIRECTORY_CONTENTS result curdir)
	file(GLOB children RELATIVE ${curdir} ${curdir}/*)
	set(dirlist "")
	foreach(child ${children})
			list(APPEND dirlist ${child})
	endforeach()
	set(${result} ${dirlist})
endmacro()

#
#	Returns the child paths of a given directory, recursively
#
macro(GET_DIRECTORY_CONTENTS_RECURSIVE out_Contents in_Path)
	set(__curDirs )
	GET_DIRECTORY_CONTENTS(__curDirs ${in_Path})

	list(TRANSFORM __curDirs PREPEND "${in_Path}/")
	list(APPEND ${out_Contents} ${__curDirs})
	foreach(lfe IN LISTS __curDirs)
		if(IS_DIRECTORY ${lfe})
			GET_DIRECTORY_CONTENTS_RECURSIVE(${out_Contents} ${lfe})
		endif()
	endforeach()
endmacro()



#
#	Returns the child paths of a given directory
#
#	@param out_Result Output variable, a list of paths will be written into it
#	@param in_DirectoryPath Directory to get children of
#
macro(GET_DIRECTORY_CONTENTS out_Result in_DirectoryPath)

	# The evaluated absolute file path
	set(__get_directory_contents_Path ${in_DirectoryPath})
	#file(REAL_PATH  __get_directory_contents_Path)

	# Holds all child paths
	set(__get_directory_contents_Children )
	file(GLOB __get_directory_contents_Children
		RELATIVE ${__get_directory_contents_Path} "${__get_directory_contents_Path}/*")

	# Write results to output variable
	set(${out_Result} ${__get_directory_contents_Children})
endmacro()



#
#	Adds a list of subdirectories to the project, pathList should be a list variable
#
macro(ADD_SUBDIRS_LIST pathList)
	foreach(lfe IN LISTS ${pathList})
		add_subdirectory(${lfe})
	endforeach()
endmacro(ADD_SUBDIRS_LIST)

#
#	Includes all subdirectories from the current source path
#
macro(ADD_SUBDIRS_HERE)
	set(dirlist )
	SUBDIRLIST(dirlist ${CMAKE_CURRENT_SOURCE_DIR})
	foreach(lfe IN LISTS dirlist)
		set(lfename )		
		get_filename_component(lfename ${lfe} NAME)
		add_subdirectory(${lfename})
	endforeach()
endmacro()

#
#	Includes all paths listed that contain CMake lists
#
#	@param rootDir Root directory path
#
function(ADD_CMAKE_SUBDIRS_FN rootDir)

	# Get subdirectories
	set(subdirList )
	SUBDIRLIST(subdirList ${rootDir})

	# Include each subdir if it has a cmake lists
	foreach(subd IN LISTS subdirList)
		if (EXISTS "${rootDir}/${subd}/CMakeLists.txt")
			add_subdirectory("${rootDir}/${subd}")
		endif()
	endforeach()

endfunction()

#
#	Includes all subdirectories containing CMake lists from the current source dir
#
macro(ADD_CMAKE_SUBDIRS_HERE)
	ADD_CMAKE_SUBDIRS_FN("${CMAKE_CURRENT_SOURCE_DIR}")
endmacro()


macro(GET_CPP_SOURCES out_sources in_directory)

	set(__cpp_source_match ".*\.[ch]$|.*\.[ch]pp$")
	set(__cpp_codegen_match ".*\.[ch]pp_in$")

	# Get directory contents
	set(__contents )
	GET_DIRECTORY_CONTENTS(__contents "${in_directory}")

	# Get list of paths that pass the given match pattern
	foreach(lfe IN LISTS __contents)
		if ("${lfe}" MATCHES "${__cpp_source_match}")
			if ("${lfe}" MATCHES "${__cpp_codegen_match}")
			else()
				list(APPEND ${out_sources} "${lfe}")
			endif()
		endif()
	endforeach()
endmacro()

macro(GET_CPP_SOURCES_HERE out_sources)
	GET_CPP_SOURCES(${out_sources} "${CMAKE_CURRENT_LIST_DIR}")
endmacro()

#
#	Adds the sources in the current directory matching a pattern to a target
#
macro(ADD_SOURCES_HERE in_Target in_MatchPattern)

	# Check that a valid target was given
	if(NOT TARGET ${in_Target})
		message(FATAL_ERROR "Cannot add sources to invalid target ${in_Target}")
	endif()

	# Root path to get source files from
	set(__add_sources_here_Path "${CMAKE_CURRENT_SOURCE_DIR}")
	
	# Get directory contents
	set(__add_sources_here_Contents )
	GET_DIRECTORY_CONTENTS(__add_sources_here_Contents "${__add_sources_here_Path}")

	# Get list of paths that pass the given match pattern
	set(__add_sources_here_SourceList )
	foreach(lfe IN LISTS __add_sources_here_Contents)
		if ("${lfe}" MATCHES "${in_MatchPattern}")
			list(APPEND __add_sources_here_SourceList "${lfe}")
		endif()
	endforeach()

	# Add sources to project
	ADD_SOURCES_LIST(${in_Target} __add_sources_here_SourceList)

endmacro()



#
#	Adds the C++ sources in the current directory to a target
#
macro(ADD_CPP_SOURCES_HERE in_Target)

	# Find sources
	set(__cpp_sources )
	GET_CPP_SOURCES_HERE(__cpp_sources)

	# Add sources to project
	ADD_SOURCES_LIST(${in_Target} __cpp_sources)

endmacro()


#
#	Gets the contents of a directory that match a given filter
#
#	@param out_Result Output variable
#	@param in_RootPath Directory to search in
#   @param in_Pattern Regex pattern used to filter which child paths are returned
#
macro(MATCH_DIRECTORY_CONTENTS out_Result in_RootPath in_Pattern) 
	set(__match_directory_contents_Raw )
	GET_DIRECTORY_CONTENTS(__match_directory_contents_Raw "${in_RootPath}")

	foreach (lfe IN LISTS __match_directory_contents_Raw)
		if ("${lfe}" MATCHES "${in_Pattern}")
			list(APPEND ${out_Result} "${lfe}")
		endif()
	endforeach()
endmacro()



set(__CPP_CODEGEN_INPUT_PATTERN "\.[ch]pp_in$")

macro(MAKE_CODEGEN_OUTPUT_FILE_NAME out_formattedName in_fileName)
	set(__make_codegen_output_file_name ${in_fileName})
	string(REPLACE ".hpp_in" ".hpp" __make_codegen_output_file_name ${__make_codegen_output_file_name})
	string(REPLACE ".cpp_in" ".cpp" __make_codegen_output_file_name ${__make_codegen_output_file_name})
	set(${out_formattedName} ${__make_codegen_output_file_name})
endmacro()

macro(CAPITALIZE out_var in_string)
	
	set(__len )
	string(LENGTH ${in_string} __len)

	set(_str ${in_string})

	set(__capitalize_FirstLetter )
	string(SUBSTRING ${_str} 0 1 __capitalize_FirstLetter)
	string(TOUPPER ${__capitalize_FirstLetter} __capitalize_FirstLetter)

	set(__remainingLen )	
	math(EXPR __remainingLen "${__len}-1")
	string(SUBSTRING ${_str} 1 ${__remainingLen} _str)

	string(PREPEND _str ${__capitalize_FirstLetter})
	set(${out_var} ${_str})
endmacro()

macro(FIND_CODEGEN_INPUTS out_listVar in_directory)
	set(_contents )
	MATCH_DIRECTORY_CONTENTS(_contents ${in_directory} ${__CPP_CODEGEN_INPUT_PATTERN})
	set(${out_listVar} ${_contents})
endmacro()

macro(CMAKE_GENERATE_CODE_FOR in_directory in_inputs)
	foreach(__input IN LISTS ${in_inputs})
		set(__output )
		MAKE_CODEGEN_OUTPUT_FILE_NAME(__output ${in_directory}/${__input})
		configure_file(${__input} ${__output})
	endforeach()
endmacro()

macro(CMAKE_GENERATE_CODE_HERE)
	set(__inputs )
	set(__dir ${CMAKE_CURRENT_LIST_DIR})
	MATCH_DIRECTORY_CONTENTS(__inputs ${__dir} ${__CPP_CODEGEN_INPUT_PATTERN})
	CMAKE_GENERATE_CODE_FOR(${__dir} __inputs)
endmacro()

macro(GET_LAST out_last in_list)
	set(__length )
	list(LENGTH ${in_list} __length)
	if (__length GREATER "0")
		set(__index 0)
		math(EXPR __index "${__length}-1")
		list(GET ${in_list} ${__index} ${out_last})
	else()
		set(${out_last} "")
	endif()
endmacro()

macro(DEINCREMENT out_var inout_var)
	math(EXPR ${out_var} "${out_var}+1")
endmacro()

macro(INCREMENT out_var in_var)
	math(EXPR ${out_var} "${in_var}+1")
endmacro()




#
# Propogate scripts directory to build
#
macro(COPY_DIRECTORY_TO_BUILD out_dirTarget in_dirName)

	set(__foo )
	GET_DIRECTORY_CONTENTS_RECURSIVE(__foo "${CMAKE_CURRENT_LIST_DIR}/${in_dirName}")
	
	add_custom_command(
		OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${in_dirName}
		COMMAND cmake -E remove_directory ${CMAKE_CURRENT_BINARY_DIR}/${in_dirName}
		COMMAND cmake -E copy_directory ${CMAKE_CURRENT_LIST_DIR}/${in_dirName} ${CMAKE_CURRENT_BINARY_DIR}/${in_dirName}
		DEPENDS ${CMAKE_CURRENT_LIST_DIR}/${in_dirName} ${__foo}
		VERBATIM
		COMMENT "Copying directory to build : \"${in_dirName}\""
		WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
	)
	add_custom_target(
		buildir_${in_dirName}
		DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/${in_dirName}
	)
	set(${out_dirTarget} buildir_${in_dirName})
endmacro()


#
# Propogate scripts directory to a specified path
#
macro(COPY_DIRECTORY_TO_PATH out_dirTarget in_dirName in_copyDestination)

	set(__foo )
	GET_DIRECTORY_CONTENTS_RECURSIVE(__foo "${CMAKE_CURRENT_LIST_DIR}/${in_dirName}")
	
	add_custom_command(
		OUTPUT ${in_copyDestination}/${in_dirName}
		COMMAND cmake -E remove_directory ${in_copyDestination}/${in_dirName}
		COMMAND cmake -E copy_directory ${CMAKE_CURRENT_LIST_DIR}/${in_dirName} ${in_copyDestination}/${in_dirName}
		DEPENDS ${CMAKE_CURRENT_LIST_DIR}/${in_dirName} ${__foo}
		VERBATIM
		COMMENT "Copying directory to build : \"${in_dirName}\""
		WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
	)
	add_custom_target(
		buildir_${in_dirName}
		DEPENDS ${in_copyDestination}/${in_dirName}
	)
	set(${out_dirTarget} buildir_${in_dirName})
endmacro()


