import argparse
import os
import re
import subprocess
import sys
import time

import config
import constants


def writeSettingLine() -> None:
    """Write the settings line to the console."""
    if config.dryrun:
        print("[dryrun] ", end="")

    if config.pull:
        print("[pull] ", end="")

    if config.fetch:
        print("[fetch] ", end="")

    if config.stash:
        print("[stash] ", end="")

    if config.checkout:
        print("[checkout] ", end="")

    if config.tidy:
        print("[tidy] ", end="")

    print("\n==========")


def getHeadBranch(dir: str):
    """Get the head branch for the given directory."""
    command = ["git", "-C", f"{dir}", "remote", "show", "origin"]
    out = subprocess.check_output(command, text=True)
    matches = re.search("HEAD branch: (?P<head>.*?)\\n", out)
    if matches:
        return matches.group("head")
    else:
        return None


def getReviewBranches(dir: str):
    """Get the review branches for the given directory."""
    command = ["git", "-C", f"{dir}", "branch"]
    out = subprocess.check_output(command, text=True)
    matches = re.findall("review/.*", out)
    return matches


def tidy(dir: str) -> None:
    """Tidy branches in the given directory."""
    review_branches = getReviewBranches(dir)
    for branch in review_branches:
        command = ["git", "-C", f"{dir}", "branch", "-D", branch]
        if config.dryrun:
            print(f"[dry] Would have run {command} in {dir}")
        else:
            print(f"[git] Deleting branch {branch}")
            try:
                p = subprocess.Popen(command, cwd=dir)
                p.wait()
                print(f"[git] Finished deleting branch {branch}")
            except Exception as e:
                print(e)
                sys.exit(2)


def git(cmd: str, dir: str, dev: bool) -> None:
    """Git commands."""
    if cmd == "pull":
        command = ["git", "-C", f"{dir}", "pull", "-q"]
    elif cmd == "fetch":
        command = ["git", "-C", f"{dir}", "fetch", "--all", "-q"]
    elif cmd == "stash":
        command = [
            "git",
            "-C",
            f"{dir}",
            "stash",
            "-m",
            f"auto_{round(time.time())}",
            "-q",
        ]
    elif cmd == "checkout":
        head = getHeadBranch(dir)
        if head is not None:
            command = ["git", "-C", f"{dir}", "checkout", head, "-q"]
        else:
            print(f"Could not determine head branch for {dir}")
            sys.exit(2)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(2)
    if config.dryrun:
        print(f"[dry] Would have run {command} in {dir}")
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
        print("[core]")
        extDir = f"{constants.MW_DIR}"
        print(f"[dir] {extDir}")
    else:
        print(f"Unknown type: {type}")
        sys.exit(2)

    # Check if it's included in the development list
    if name in constants.IN_DEVELOPMENT:
        print("[dev] Marked as in development")
        devExt = True

    if config.stash is True:
        git("stash", extDir, devExt)
    if config.fetch is True:
        git("fetch", extDir, devExt)
    if config.checkout is True:
        git("checkout", extDir, devExt)
    if config.pull is True:
        git("pull", extDir, devExt)
    if config.tidy is True and devExt is False:
        tidy(extDir)
    print()


def walkDir(directory: str, type: str) -> None:
    for name in os.listdir(directory):
        if os.path.isdir(f"{directory}{name}"):
            doWork(name, type)


def main(argv):
    """Main function."""
    print(f"gitGud v{constants.VERSION}", "==========", sep="\n")

    parser = argparse.ArgumentParser(
        prog="gitGud",
        description="""Manage MediaWiki extensions and skins when locally developing.\nRunning without any arguments will sync core, skins and extensions without any tidying or checking out.""",
        usage="%(prog)s [options]",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-t",
        "--tidy",
        default=config.tidy,
        help="Tidy up branches",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--dryrun",
        default=config.dryrun,
        help="Don't make any changes",
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--checkout",
        default=config.checkout,
        help="Checkout the HEAD branch",
        action="store_true",
    )
    parser.add_argument(
        "-f",
        "--fetch",
        default=config.fetch,
        help="Fetch all branches",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--stash",
        default=config.stash,
        help="Stash any changes",
        action="store_true",
    )
    parser.add_argument(
        "--pull", default=config.pull, help="Pull changes", action="store_true"
    )
    parser.add_argument(
        "--debug", default=False, help="Debug stuff", action="store_true"
    )
    args = parser.parse_args()

    # Ew
    config.tidy = args.tidy
    config.dryrun = args.dryrun
    config.checkout = args.checkout
    config.fetch = args.fetch
    config.pull = args.pull
    config.stash = args.stash

    writeSettingLine()
    # TODO: Remove for release
    if args.debug:
        for arg in args.__dict__:
            print(f"{arg}: {args.__dict__[arg]}")
        sys.exit()

    # Run on core
    doWork("core", "core")
    # Run on extensions and skins
    walkDir(constants.EXT_DIR, "extension")
    walkDir(constants.SKIN_DIR, "skin")
    print(
        "Completed — you may need to run `composer update` and `maintenance/update.php`"
    )


if __name__ == "__main__":
    main(sys.argv[1:])
