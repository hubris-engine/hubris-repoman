import subprocess

import re
import hubris
import hubris.filesystem as fs
from hubris.filesystem import Path as Path



_FATAL_BRANCH_REGEX = re.compile("fatal:")
_ERROR_BRANCH_REGEX = re.compile("error:")
_BRANCH_COMMAND_SPECIAL_REGEX = re.compile("\-[dDm]")

_STATUS_MODIFIED = "modified:"
_STATUS_NEW_FILE = "new file:"
_STATUS_DELETED  = "deleted:"
_STATUS_MODIFIED_REGEX = re.compile(_STATUS_MODIFIED)
_STATUS_NEW_FILE_REGEX = re.compile(_STATUS_NEW_FILE)
_STATUS_DELETED_REGEX = re.compile(_STATUS_DELETED)
_PROCESS_STATUS_REGEX = re.compile("[^ ]+")


def _check_stderr(stream : str) -> bool:
	m = _FATAL_BRANCH_REGEX.search(stream)
	if m is not None:
		return False
	m = _ERROR_BRANCH_REGEX.search(stream)
	if m is not None:
		return False
	return True

def _process_stdout(stream : str) -> str:
	return stream.strip()
def _process_stderr(stream : str) -> str:
	return stream.strip()

def _proc_output(command : "list[str]", stdout : str, stderr : str, quiet : bool = False):
	
	cmd_git = command.pop(0)
	cmd_name = command.pop(0)
	if cmd_name == "-C":
		command.pop(0)
		cmd_name = command.pop(0)

	cmd_args = command

	cmdstr = ""
	cmdstr = cmd_git + " " + cmd_name

	if cmd_name == "branch" and len(cmd_args) != 0:
		m = _BRANCH_COMMAND_SPECIAL_REGEX.match(cmd_args[0])
		if m is not None:
			cmdstr += " " + str(m.group(0))

	if not _check_stderr(stderr):
		if not quiet and len(stderr) != 0:
			hubris.log_error(f'{cmdstr}\n\t{_process_stderr(stderr)}')
		return False

	if not quiet and len(stdout) != 0:
		hubris.log_info(f'{cmdstr}\n\t{_process_stdout(stdout)}')
	return True


def branch(repo_root : "str | Path" = ".", quiet : bool = False):
	command = [
		"git",
		"-C", str(repo_root),
		"branch"
	]
	proc = subprocess.Popen(command,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True)
	
	proc_stdout, proc_stderr = proc.communicate()
	proc.wait()

	# Check for errors
	if not _proc_output(command, proc_stdout, proc_stderr, quiet=quiet):
		return None

	# Parse current branch

	current_branch = ""
	branches = []

	lines = proc_stdout.splitlines(False)
	for v in lines:
		s = v.strip()
		if s.startswith("*"):
			s = s.removeprefix("*").strip()
			current_branch = s
		branches.append(s)

	return current_branch, branches

def rename_branch(new_name : str, repo_root : "str | Path" = ".", quiet : bool = False) -> bool :
	
	command = [
			"git",
			"-C", str(repo_root),
			"branch",
			"-m",
			str(new_name)
	]
	proc = subprocess.Popen(command,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True)
	
	proc_stdout, proc_stderr = proc.communicate()
	proc.wait()

	# Check for errors
	if not _proc_output(command, proc_stdout, proc_stderr, quiet=quiet):
		return False

	return True
	
def delete_branch(branch_name : str, force : bool = False, repo_root : "str | Path" = ".", quiet : bool = False) -> bool :
	command = [
		"git",
		"-C", str(repo_root),
		"branch",
	]
	if force:
		command.append("-D")
	else:
		command.append("-d")
	command.append(str(branch_name))

	proc = subprocess.Popen(command,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True)
	
	proc_stdout, proc_stderr = proc.communicate()
	proc.wait()

	# Check for errors
	if not _proc_output(command, proc_stdout, proc_stderr, quiet=quiet):
		return False
	return True

def create_branch(branch_name : str, repo_root : "str | Path" = ".", quiet : bool = False) -> bool :
	command = [
		"git",
		"-C", str(repo_root),
		"branch",
		str(branch_name)
	]

	proc = subprocess.Popen(
		command,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True)
	
	proc_stdout, proc_stderr = proc.communicate()
	proc.wait()

	# Check for errors
	if not _proc_output(command, proc_stdout, proc_stderr, quiet=quiet):
		return False
		
	return True

def checkout(branch_name : str, repo_root : "str | Path" = ".", quiet : bool = False) -> bool :

	command = [
		"git",
		"-C", str(repo_root),
		"checkout",
		"-q"
	]
	command.append(str(branch_name))

	proc = subprocess.Popen(
		command,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True)
	
	proc_stdout, proc_stderr = proc.communicate()
	proc.wait()

	# Check for errors
	if not _proc_output(command, proc_stdout, proc_stderr, quiet=quiet):
		return False
	return True


class ChangeType:
	modified = "modified"
	new = "new file"
	deleted = "deleted"

class Change:
	def __str__(self) -> str :
		return str(self.file)
	def __init__(self, file : "Path | str", type : ChangeType):
		self.file = Path(file)
		self.type = type

class StatusResult:
	def __init__(self, staged : "list[Change]" = [], unstaged : "list[Change]" = []):
		self.staged : "list[Change]" = staged
		self.unstaged : "list[Change]" = unstaged
		
		self.all : "list[Change]" = []
		self.all.extend(staged)

		for v in unstaged:
			found = False
			for q in self.all:
				if v.file == q.file:
					found = True
					break
			if not found:
				self.all.append(v)




def status(repo_root : "str | Path" = ".", quiet : bool = False) -> "StatusResult | None" :

	command = [
		"git",
		"-C", str(repo_root),
		"status",
	]
	proc = subprocess.Popen(
		command,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True)
	
	proc_stdout, proc_stderr = proc.communicate()
	proc.wait()

	# Check for errors
	if not _proc_output(command, proc_stdout, proc_stderr, quiet=quiet):
		return None

	# Parse modified files list
	staged = []
	unstaged = []
	
	def push_staged(c):
		staged.append(c)
	def push_unstaged(c):
		unstaged.append(c)
	def push_other(c):
		return


	push = push_other

	lines = proc_stdout.splitlines()
	for v in lines:
		s = v.strip()
		
		if s.startswith("Changes to be committed:"):
			push = push_staged
		elif s.startswith("Changes not staged for commit:"):
			push = push_unstaged
		elif s.startswith("Untracked files:"):
			push = push_other

		m = _STATUS_MODIFIED_REGEX.search(s)
		if m is not None:
			s = s.removeprefix(_STATUS_MODIFIED).strip()
			m = _PROCESS_STATUS_REGEX.search(s)
			if m is not None:
				s = str(m.group(0))
			push(Change(s, ChangeType.modified))
			continue
		
		m = _STATUS_NEW_FILE_REGEX.search(s)
		if m is not None:
			s = s.removeprefix(_STATUS_NEW_FILE).strip()
			m = _PROCESS_STATUS_REGEX.search(s)
			if m is not None:
				s = str(m.group(0))
			push(Change(s, ChangeType.new))
			continue
		
		m = _STATUS_DELETED_REGEX.search(s)
		if m is not None:
			s = s.removeprefix(_STATUS_DELETED).strip()
			m = _PROCESS_STATUS_REGEX.search(s)
			if m is not None:
				s = str(m.group(0))
			push(Change(s, ChangeType.deleted))
			continue
		
	return StatusResult(staged, unstaged)

def add(pattern : "str", repo_root : "str | Path" = ".", quiet : bool = False) -> bool :

	command = [
		"git",
		"-C", str(repo_root),
		"add",
		str(pattern)
	]
	
	proc = subprocess.Popen(
		command,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True)
	
	proc_stdout, proc_stderr = proc.communicate()
	proc.wait()

	# Check for errors
	if not _proc_output(command, proc_stdout, proc_stderr, quiet=quiet):
		return False

	return True


def commit(message : str = "", repo_root : "str | Path" = ".", quiet : bool = False) -> bool :

	command = [
		"git",
		"-C", str(repo_root),
		"commit",
		"-m", str(message)
	]
	
	proc = subprocess.Popen(
		command,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True)
	
	proc_stdout, proc_stderr = proc.communicate()
	proc.wait()

	# Check for errors
	if not _proc_output(command, proc_stdout, proc_stderr, quiet=quiet):
		return False

	return True

def push(auto_set_upstream : bool = False, remote_name : str = "origin", repo_root : "str | Path" = ".", quiet : bool = False) -> bool :
	
	command = [
		"git",
		"-C", str(repo_root),
		"push"
	]

	if auto_set_upstream:
		_branch, _ = branch(repo_root=repo_root, quiet=quiet)
		command.extend(["--set-upstream", str(remote_name), str(_branch)])
			
	proc = subprocess.Popen(
		command,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True)
	
	proc_stdout, proc_stderr = proc.communicate()
	proc.wait()

	# Check for errors
	if not _proc_output(command, proc_stdout, proc_stderr, quiet=quiet):
		return False

	return True

def pull(auto_set_upstream : bool = False, remote_name : str = "origin", repo_root : "str | Path" = ".", quiet : bool = False) -> bool :

	command = [
		"git",
		"-C", str(repo_root),
		"pull"
	]
	
	proc = subprocess.Popen(
		command,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True)
	
	proc_stdout, proc_stderr = proc.communicate()
	proc.wait()

	# Check for errors
	if not _proc_output(command, proc_stdout, proc_stderr, quiet=quiet):
		return False

	return True



def is_local_repo(repo_root : "str | fs.Path" = ".") -> bool :
	"""
	Checks if a directory is a git repository.
	"""
	# Fix arg
	repo_root = Path(repo_root).resolve()

	# Ensure we got a directory path
	if not repo_root.is_dir():
		return False

	# Look for a .git directory
	repo_git_dir_path = repo_root.joinpath(".git")
	if repo_git_dir_path.exists() and repo_git_dir_path.is_dir():
		return True
	else:
		# I know returning bool like this is stupid and I could just evaluate the if condition.
		# It's probably seems reasonably that I am using python and would therefore think this is fine.
		# 
		# Fuck off, I'll write an "is_even()" function next
		return False

