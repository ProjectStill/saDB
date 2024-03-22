import sadb_classes
import database
import yaml_parse
import click
import configuration as cfg

CONFIG = cfg.SadbConfig()

# Commandline Interface
@click.group()  # click group to allow subcommands
def cli():
    pass


@click.command()
def update():
    pass