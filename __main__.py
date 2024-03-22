import sadb_classes
import database
import yaml_parse
import click



# Commandline Interface
@click.group()  # click group to allow subcommands
def cli():
    pass

@click.command()
def update_db():
    pass