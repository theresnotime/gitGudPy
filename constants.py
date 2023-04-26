import typing

from environs import Env

env = Env()
env.read_env()

# Meta
VERSION = "1.0.0"
GITHUB = "https://github.com/theresnotime/gitGudPy"

# Development repos
IN_DEVELOPMENT = env.list("IN_DEVELOPMENT")

# Directory config
MW_DIR = typing.cast(str, env.str("MW_DIR"))
EXT_DIR = typing.cast(str, f"{MW_DIR}extensions")
SKIN_DIR = typing.cast(str, f"{MW_DIR}skins")
