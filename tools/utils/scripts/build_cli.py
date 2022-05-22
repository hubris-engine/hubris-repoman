from argparse import ArgumentParser
from hubris.repoman import RepoMan
import hubris

from repo import clean, build, getdeps

parser = ArgumentParser(description="Management for the repo in one nice CLI")
parser.add_argument("--verbose", help="Allow all logging", action="store_true", default=False)
parser.add_argument("--getdeps", help="Installs dependencies, this should be run after a fresh clone",
	action="store_true", default=False)

group = parser.add_mutually_exclusive_group()
group.add_argument("-c", "--clean", help="Cleans the repo", action="store_true", default=False)
group.add_argument("-x", "--rebuild", help="Cleans and then builds the repo", action="store_true", default=False)
group.add_argument("-b", "--build", help="Builds the repo", action="store_true", default=False)

args = parser.parse_args()


steps = []

if args.getdeps:
	def getdeps_step():
		return getdeps(force = True)
	steps.insert(0, getdeps_step)

if args.clean:
	steps.extend([clean])
elif args.build:
	steps.extend([build])
elif args.rebuild:
	steps.extend([clean, build])
else:
	steps.extend([build])

if args.verbose:
	hubris.set_log_level(hubris.LogLevel.all)
else:
	hubris.set_log_level(hubris.LogLevel.warn)

for v in steps:
	if not v():
		hubris.log_error("Failed to interact with repo")
		exit(1)
