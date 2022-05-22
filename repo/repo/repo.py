import os
from pathlib import Path
import re
import hubris
import hubris.repoman as repo
import hubris.platform as platform 

_VULKAN_SDK_VERSION_REGEX = re.compile("[\.0-9]+$")


build_root = "_build"
install_root = "_install"

artifact_paths = [
	build_root,
	install_root,
	"_doxygen",
	"out",
]

deps = {
	"windows" : [
		"ninja",
		"vulkan-sdk",
		"llvm"
	],
	"linux" : [
		"ninja-build",
		"libxrandr-dev",
		"libxinerama-dev",
		"libxcursor-dev",
		"libxi-dev",
		"libvulkan-dev",
		"clang"
	]
}


defs = []

defs.extend([

	# TODO : Improve this please.
	#"C:/Program Files (x86)/Windows Kits/10",

	repo.CMakeDef("GLFW_BUILD_EXAMPLES", False),
	repo.CMakeDef("GLFW_BUILD_TESTS", False),
	repo.CMakeDef("GLFW_BUILD_DOCS", False),
	repo.CMakeDef("GLFW_INSTALL", False),

	repo.CMakeDef("LUA_INSTALL", False),
])

rman = repo.RepoMan()
rman.artifact_paths = artifact_paths

target_os = platform.get_os()
if target_os == platform.OS.windows:
	rman.deps = deps["windows"]
elif target_os == platform.OS.linux:
	rman.deps = deps["linux"]



def _determine_vulkan_sdk_path_windows():
	""" Find vulkan SDK verisons downloaded and determines which one to use. """
	cwd = Path().cwd()
	vulkan_sdk_versions = []
	vulkan_sdk_root = Path(cwd.drive + cwd.root).joinpath("VulkanSDK")
	for v in vulkan_sdk_root.iterdir():
		match = _VULKAN_SDK_VERSION_REGEX.search(v.name)
		if match:
			vulkan_sdk_versions.append({ match.group(0) })
	if len(vulkan_sdk_versions) != 0:
		return vulkan_sdk_root.joinpath(str(vulkan_sdk_versions[0]))		
	return None


def clean():
	result = rman.clean()
	if not result:
		hubris.log_error("Failed to clean repo")
	return result

def build():
	
	env = os.environ
	
	# Handle vulkan sdk
	vulkan_sdk = env.get("VULKAN_SDK", None)
	if vulkan_sdk is not None:
		defs.append(repo.CMakeDef("VULKAN_SDK", str(vulkan_sdk)))
	else:
		if target_os == platform.OS.windows:
			_vulkanSDK = _determine_vulkan_sdk_path_windows()
			env["VULKAN_SDK"] = _vulkanSDK

	result = rman.build(
		build_root=build_root,
		source_root=".",
		defs=defs,
		env=env
	)
	if not result:
		hubris.log_error("Failed to build repo")
		return result

	result = rman.install(build_root=build_root)
	if not result:
		hubris.log_error("Failed to install repo")
		return result

	return result

def getdeps(force = False):
	result = rman.getdeps(force)
	if not result:
		hubris.log_error("Failed to get repo dependencies")
	if force:
		return True
	return result
