#
#	Homebrew C++ Dependency Handling
#




# Find Git
find_package(Git QUIET)

# Check that Git was found and notify
if (Git_FOUND)
	message(STATUS "Found Git")
else()
	# If git wasn't found, start yelling ?
	message(FATAL_ERROR "Failed to find Git")
endif()

#
#	Executes a command to clone a git repository
#
#	Takes an optional 3rd argument that specifies the branch to clone.
#
macro(DEPGET_CLONE_GIT_REPOSITORY_EXECUTE in_Repo in_CloneDest)
	
	set(__command ${GIT_EXECUTABLE} clone ${in_Repo} ${in_CloneDest})
	if (${ARGC} EQUAL 3)
		set(__command ${__command} -b ${ARGV2})
		message(FATAL_ERROR "${__command}")
	endif()

	execute_process (
		COMMAND ${__command}
		RESULTS_VARIABLE __gitResultCode
		ERROR_VARIABLE __gitResultError
		WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
		COMMAND_ECHO STDOUT
	)
	if (NOT __gitResultCode EQUAL "0")
		message(FATAL_ERROR "Failed to clone repository -\n${__gitResultError}")
	endif()
endmacro()

#
#	Executes a command to clone a git repository if the clone destination directory does not exist
#
macro(DEPGET_CLONE_GIT_REPOSITORY in_Repo in_CloneDest)
	DEPGET_CLONE_GIT_REPOSITORY_EXECUTE(${ARGV})
endmacro()


macro(DEPGET_ADD_GIT_TARGET in_TargetName in_Repo in_CloneDest)

	# Try and include the cloned directory if possible.
	if (EXISTS "${in_CloneDest}/CMakeLists.txt")
		add_subdirectory(${in_CloneDest})
		if (NOT TARGET ${in_TargetName})
			message(WARNING "Git dependency target \"${in_TargetName}\" is not defined but its cmake lists is present, is the name given incorrect?")
		endif()
	endif()
	
	# Clone if not defined.
	if (NOT TARGET ${in_TargetName})
		DEPGET_CLONE_GIT_REPOSITORY(${in_Repo} ${in_CloneDest} ${ARGN})
		if (EXISTS "${in_CloneDest}/CMakeLists.txt")
			add_subdirectory(${in_CloneDest})
		endif()
	endif()

endmacro()
