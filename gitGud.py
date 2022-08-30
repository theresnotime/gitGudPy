import getopt
import sys

import config

__version__ = config.VERSION

tidy = False
dryrun = False
checkout = False
override = False
sync = True


def writeHelp():
    """Write the help text to the console."""
    print(
        "Usage: gitGud.py [ -t, --tidy ] [ -d, --dryrun ] [ -c, --checkout ]",
        "Running without any arguments will sync core, skins",
        "and extensions without any tidying or checking out.",
        "==========",
        f"{config.GITHUB}",
        sep="\n",
    )


def writeSettingLine():
    """Write the settings line to the console."""
    if tidy:
        print("[tidy] ", end="")

    if dryrun:
        print("[dryrun] ", end="")

    if checkout:
        print("[checkout] ", end="")

    if sync:
        print("[sync]")

    print("==========")


def main(argv):
    """Main function."""
    global tidy, dryrun, checkout, sync
    print(f"gitGud v{__version__}", "==========", sep="\n")

    try:
        opts, args = getopt.getopt(argv, "htdc", ["help", "tidy", "dryrun", "checkout"])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            writeHelp()
            sys.exit()
        elif opt in ("-t", "--tidy"):
            tidy = True
        elif opt in ("-d", "--dryrun"):
            dryrun = True
        elif opt in ("-c", "--checkout"):
            checkout = True

    writeSettingLine()


if __name__ == "__main__":
    main(sys.argv[1:])
