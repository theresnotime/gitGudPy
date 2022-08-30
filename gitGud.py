import getopt
import os
import subprocess
import sys

import config
import constants


def writeHelp() -> None:
    """Write the help text to the console."""
    print(
        "Usage: gitGud.py [ -t, --tidy ] [ -d, --dryrun ] [ -c, --checkout ]",
        "Running without any arguments will sync core, skins",
        "and extensions without any tidying or checking out.",
        "==========",
        f"{constants.GITHUB}",
        sep="\n",
    )


def writeSettingLine() -> None:
    """Write the settings line to the console."""
    if config.tidy:
        print("[tidy] ", end="")

    if config.dryrun:
        print("[dryrun] ", end="")

    if config.checkout:
        print("[checkout] ", end="")

    if config.sync:
        print("[sync]")

    print("==========")


def git(cmd: str, dir: str, dev: bool) -> None:
    """Git commands."""
    if cmd == "pull":
        command = ["git", "-C", f"{dir}", "pull", "-q"]
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(2)

    if config.dryrun:
        print(f"[dry] Would have run git {cmd} in {dir}")
    else:
        print(f"[git] Running git {cmd}")
        try:
            p = subprocess.Popen(command, cwd=dir)
            p.wait()
            print(f"[git] Finished running git {cmd}")
        except Exception as e:
            print(e)
            sys.exit(2)


def doWork(name: str, type: str) -> None:
    """Do work on the given extension/skin"""
    devExt = False
    # Get the type
    if type == "extension":
        print(f"[ext:{name}]")
        extDir = f"{constants.EXT_DIR}{name}"
        print(f"[dir] {extDir}")
    elif type == "skin":
        print(f"[skin:{name}]")
        extDir = f"{constants.SKIN_DIR}{name}"
        print(f"[dir] {extDir}")
    elif type == "core":
        pass
    else:
        print(f"Unknown type: {type}")
        sys.exit(2)

    # Check if it's included in the development list
    if name in constants.IN_DEVELOPMENT:
        print("[dev] Marked as in development")
        devExt = True

    git("pull", extDir, devExt)
    print()


def walkDir(directory: str, type: str) -> None:
    for name in os.listdir(directory):
        if os.path.isdir(f"{directory}{name}"):
            doWork(name, type)


def main(argv):
    """Main function."""
    print(f"gitGud v{constants.VERSION}", "==========", sep="\n")

    try:
        opts, args = getopt.getopt(argv, "htdc", ["help", "tidy", "dryrun", "checkout"])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            writeHelp()
            sys.exit()
        elif opt in ("-t", "--tidy"):
            config.tidy = True
        elif opt in ("-d", "--dryrun"):
            config.dryrun = True
        elif opt in ("-c", "--checkout"):
            config.checkout = True

    writeSettingLine()
    walkDir(constants.EXT_DIR, "extension")
    walkDir(constants.SKIN_DIR, "skin")


if __name__ == "__main__":
    main(sys.argv[1:])
