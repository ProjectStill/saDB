# saDB

saDB is a solution for managing app sources and databases for stillOS. When paired with stillAppMan, it can be used by distro vendors to moderate apps from third party sources without maintaining their own repos.

## Dependencies
saDB requires the following python dependencies to be installed:
- click (for CLI)
- tqdm (for download progress bars)
- unittest (for testing)

## CLI Usage
If you are running stillOS, everything here is automated and you will not need to use the CLI unless something goes wrong.

The project provides several commands:

- `check_sources`: Tests to make sure all sources are correctly configured.
- `update_source`: Downloads source data and generates source files. This command must be run as root.
- `update_db`: Updates the database with the latest YAML data.
- `update`: Runs both `update_source` and `update_db`. This command requires root.
- `get_db_location`: Outputs the location of the database.
- `run_tests`: Runs the tests for the program.

You can run these commands as follows:

```bash
python src/__main__.py <command>
```

Replace `<command>` with any of the commands listed above.

## Running the tests

You can run the tests using the `run_tests` command:

## TODO:
- [ ] Add Tags for stillCenter
- [ ] Allow managing per user sources
- [ ] Snap support