import sadb_classes
import database
import yaml_parse
import configuration as cfg
import utilities as util

import click

CONFIG = cfg.SadbConfig()

# Commandline Interface
@click.group()  # click group to allow subcommands
@click.option("--verbose", is_flag=True, help="Enable verbose output")
def cli(verbose):
    CONFIG.verbose = verbose


@click.command()
def update():
    # Download yaml database
    if CONFIG.verbose:
        print("Checking for database updates (1/3):")
    if CONFIG.verbose:
        print("Downloading yaml database (2/3):")
    yaml = util.download_yaml(CONFIG.repo_url, verbose=CONFIG.verbose)
    # Add apps to database
    if CONFIG.verbose:
        print("Regenerating database (3/3):")
    with database.WritableDB(CONFIG) as db:
        db.clear_db()
        db.add_apps(yaml_parse.get_apps_from_yaml(yaml))


@click.command()
def get_db_location():
    print(CONFIG.db_location)


@click.command()
def check_sources():


cli.add_command(update)