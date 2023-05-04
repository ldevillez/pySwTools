"""
Help manage the config of the tool

Taken from: https://github.com/jeertmans/selsearch/blob/main/selsearch/config.py
"""

import os
from pathlib import Path

import click
import rtoml as toml
from appdirs import user_config_dir
from pydantic import BaseModel

Shortcut = str
UrlAlias = str


# pylint: disable=too-few-public-methods
class Config(BaseModel):  # type: ignore
    """Config object"""

    sw_version: int = 2022

    @classmethod
    def parse_toml(cls, file: Path) -> "Config":
        """
        parse the toml object to a config file
        """
        return cls.parse_obj(toml.loads(file.read_text()))  # type: ignore


def get_config_dir() -> Path:
    """Get the config dir of the project"""
    return Path(user_config_dir("pyswtools", "ldevillez"))


def get_config_file(config_dir: Path) -> Path:
    """Get the config path file"""
    return config_dir.joinpath("pyswtools.toml")


def get_config() -> Config:
    """
    Read the config file if it exists, otherwise use the default value of the config
    """
    config_file = get_config_file(get_config_dir())

    if os.path.exists(config_file):
        return Config.parse_toml(config_file)
    return Config()


@click.command()
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="If set, overwrite any existing config file.",
)
@click.help_option("-h", "--help")
def init(force: bool) -> None:
    """
    Initialize config file and return its path.
    """
    config_dir = get_config_dir()
    config_file = get_config_file(config_dir)

    if not force and config_file.exists():
        raise click.UsageError(
            f"Config file `{str(config_file)}` already exists. To overwrite it, use `--force` option."
        )

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    toml.dump(Config().dict(), config_file)

    click.secho(f"Successfully created config file `{str(config_file)}`.", fg="green")


@click.command()
@click.help_option("-h", "--help")
@click.option(
    "--path",
    is_flag=True,
    default=False,
    help="If set, get the path to the config",
)
def dump(path: bool) -> None:
    """
    Dump the config file to stdout or its path
    """
    if path:
        config_dir = get_config_dir()
        config_file = get_config_file(config_dir)
        click.echo(config_file)

    else:
        conf = get_config().dict()

        click.echo(toml.dumps(conf))


@click.command()
@click.help_option("-h", "--help")
@click.argument(
    "name",
    type=click.STRING,
)
@click.argument(
    "value",
)
def set_value(name: str, value) -> None:
    """
    Update the config file to update a value
    """
    config_dir = get_config_dir()
    config_file = get_config_file(config_dir)

    if config_file.exists():
        conf = get_config().dict()
        if name not in conf.keys():
            click.echo(f"The config value {name} does not exists")
        else:
            conf[name] = value
            toml.dump(conf, config_file)
            click.echo(f"{name} set to {value}")
    else:
        click.echo(
            "No pyswtools.toml exists cannot update its value. Call the init command first."
        )


@click.group()
@click.help_option("-h", "--help")
def config() -> None:
    """
    Combination of commands to help you work with solidworks
    """


config.add_command(init)
config.add_command(dump)
config.add_command(set_value)
