from typing import List, Optional

import sqlite3
import sadb
import sadb.utilities as utilities
from sadb.configuration import SadbConfig
import os.path
from urllib.parse import urlparse, urlunparse

# Shortened alias functions
tcsl = sadb.to_csl
fcsl = sadb.from_csl

# Function to check if the database is in the correct format
def is_valid_sqlite_db(path) -> bool:
    """
    Checks if the SQLite database at the specified path is valid.

    Returns:
        bool: True if the database is valid, False otherwise.
    """
    out = True
    conn = None
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
    except sqlite3.Error:
        out = False
    finally:
        if conn:
            conn.close()
        return out


def remove_duplicate_apps(apps: List[sadb.App]) -> List[sadb.App]:
    unique_apps = {}
    for app in apps:
        if app.src_pkg_name not in unique_apps:
            unique_apps[app.src_pkg_name] = app
    return list(unique_apps.values())


# Read-only version of the database
class ReadableDB:
    """
    A class used to represent a read-only SQLite database.

    ...

    Attributes
    ----------
    conn : sqlite3.Connection
        a SQLite connection object
    c : sqlite3.Cursor
        a SQLite cursor object

    Methods
    -------
    get_app(app_id: str) -> sadb.App:
        Returns the app with the given id from the database.
    column_to_app(column: tuple):
        Converts a SQL query result to an App class instance.
    get_all_apps() -> list:
        Returns all apps from the database.
    get_apps_from_query(query: str) -> list:
        Executes the given SQL query and returns the result as a list of App class instances.
    """
    def __init__(self, config: SadbConfig, init_db: bool = True):
        """
        Constructs a new ReadableDB instance.

        Parameters:
            config (SadbConfig): The configuration for the database.
            init_db (bool): Whether to initialize the database connection. Default is True.
        """
        if init_db:  # used to prevent init of the connection for writable db
            # Use uri workaround to open in read-only mode
            file_uri = urlunparse(urlparse(os.path.abspath(config.db_location))._replace(scheme='file')) + "?mode=ro"
            self.conn = sqlite3.connect(file_uri, uri=True)
            self.c = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.conn.close()

    def get_app(self, app_id: str) -> Optional[sadb.App]:
        """
        Returns the app with the given id from the database.

        Parameters:
            app_id (str): The id of the app.

        Returns:
            sadb.App: The app with the given id.
        """
        self.c.execute("SELECT * FROM apps WHERE id=?", (app_id, ))
        app = self.c.fetchone()
        if app is None:
            return None
        return self.column_to_app(app)

    def get_installed_app_from_main_db(self, source: str, package: str) -> Optional[sadb.App]:
        """
        Returns the app with the given id from the database.

        Parameters:
            app_id (str): The id of the app.

        Returns:
            sadb.App: The app with the given id.
        """
        self.c.execute("SELECT * FROM apps WHERE primary_src=? AND src_pkg_name=?", (source, package))
        app = self.c.fetchone()
        if app is None:
            return None
        return self.column_to_app(sadb.InstalledApp.from_app(app))

    @staticmethod
    def column_to_app(column: tuple):
        """
        Converts a SQL query result to an App class instance.

        Parameters:
            column (tuple): The SQL query result.

        Returns:
            sadb.App: The App class instance.
        """
        assert len(column) == 21
        return sadb.App(
            column[0], column[1], column[2], column[3], column[4], column[5],
            column[6], column[7], fcsl(column[8]), fcsl(column[9]), fcsl(column[10]),
            column[11], sadb.Pricing(column[12]), sadb.MobileType((column[13])),
            sadb.StillRating(column[14]), column[15], column[16], column[17], fcsl(column[18]),
            column[19], fcsl(column[20])
        )

    def get_all_apps(self) -> list:
        """
        Returns all apps from the database.

        Returns:
            list: The list of all apps.
        """
        self.c.execute("SELECT * FROM apps")
        return [self.column_to_app(app) for app in self.c.fetchall()]

    def get_apps_from_query(self, query: str) -> list:
        """
        Executes the given SQL query and returns the result as a list of App class instances.

        Parameters:
            query (str): The SQL query.

        Returns:
            list: The list of App class instances.
        """
        self.c.execute(query)
        return [self.column_to_app(app) for app in self.c.fetchall()]


class WritableDB(ReadableDB):
    """
    A class used to represent a writable SQLite database.

    ...

    Attributes
    ----------
    conn : sqlite3.Connection
        a SQLite connection object
    c : sqlite3.Cursor
        a SQLite cursor object

    Methods
    -------
    create_db():
        Creates the database if it does not exist.
    add_app(app: sadb.App) -> None:
        Adds the given app to the database.
    add_apps(apps: List[sadb.App]) -> None:
        Adds the given list of apps to the database.
    clear_db() -> None:
        Deletes all apps from the database.
    """
    def __init__(self, config: SadbConfig):
        """
        Constructs a new WritableDB instance.

        Parameters:
            config (SadbConfig): The configuration for the database.
        """
        new_db = not os.path.exists(config.db_location)
        # Create folders for database if they don't exist
        if new_db and not os.path.exists(os.path.dirname(config.db_location)):
            os.makedirs(os.path.dirname(config.db_location), exist_ok=True)
            if utilities.is_sudo_root():
                utilities.fix_perms(os.path.dirname(config.db_location))

        self.conn = sqlite3.connect(config.db_location)
        self.c = self.conn.cursor()
        if new_db:
            self.create_db()
            if utilities.is_sudo_root():
                utilities.fix_perms(config.db_location)
        super().__init__(config, init_db=False)

    def create_db(self):
        """
        Creates the database if it does not exist.
        """
        self.c.execute('''CREATE TABLE IF NOT EXISTS apps
            (id text, name text, primary_src text, src_pkg_name text, icon_url text, 
            author text, summary text, description text, categories text, keywords text, 
            mimetypes text, license text, pricing int, mobile int, still_rating int, 
            still_rating_notes text, homepage text, donate_url text, screenshot_urls text, 
            demo_url text, addons text)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS installed
            (id text, name text, primary_src text, src_pkg_name text, icon_url text, 
            author text, summary text, description text, categories text, keywords text, 
            mimetypes text, license text, pricing int, mobile int, still_rating int, 
            still_rating_notes text, homepage text, donate_url text, screenshot_urls text, 
            demo_url text, addons text, update_available int)''')

    def add_app(self, app: sadb.App) -> None:
        """
        Adds the given app to the database.

        Parameters:
            app (sadb.App): The app to add.
        """
        # Prevent apps with the same package name
        self.c.execute("SELECT * FROM apps WHERE src_pkg_name=?", (app.src_pkg_name,))
        if self.c.fetchone() is not None:
            raise ValueError(f"An app with src_pkg_name {app.src_pkg_name} already exists.")
        self.c.execute("INSERT OR REPLACE INTO apps VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                app.app_id, app.name, app.primary_src, app.src_pkg_name, app.icon_url,
                app.author, app.summary, app.description, tcsl(app.categories),
                tcsl(app.keywords), tcsl(app.mimetypes), app.app_license, app.pricing.value,
                app.mobile.value, app.still_rating.value, app.still_rating_notes, app.homepage,
                app.donate_url, tcsl(app.screenshot_urls), app.demo_url, tcsl(app.addons)
            )
        )
        self.conn.commit()

    def add_apps(self, apps: List[sadb.App]) -> None:
        """
        Adds the given list of apps to the database.

        Parameters:
            apps (list): The list of apps to add.
        """
        # Removing duplicate package names
        self.c.execute("SELECT src_pkg_name FROM apps")
        existing_pkgs = [row[3] for row in self.c.fetchall()]
        apps = remove_duplicate_apps(apps)
        apps_data = [
            (
                app.app_id, app.name, app.primary_src, app.src_pkg_name, app.icon_url,
                app.author, app.summary, app.description, tcsl(app.categories),
                tcsl(app.keywords), tcsl(app.mimetypes), app.app_license, app.pricing.value,
                app.mobile.value, app.still_rating.value, app.still_rating_notes, app.homepage,
                app.donate_url, tcsl(app.screenshot_urls), app.demo_url, tcsl(app.addons)
            ) for app in apps if app.src_pkg_name not in existing_pkgs
        ]
        self.c.executemany("INSERT OR REPLACE INTO apps VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", apps_data)
        self.conn.commit()

    def clear_db(self) -> None:
        """
        Deletes all apps from the database.
        """
        self.c.execute("DELETE FROM apps")
        #  self.conn.commit()  REMOVE COMMIT INCASE FUTURE OPERATION IS UNSUCCESSFUL

    def clear_installed_apps(self) -> None:
        """
        Clears the installed app daatbaase
        """
        self.c.execute("DELETE FROM installed")
        #  self.conn.commit()  REMOVE COMMIT INCASE FUTURE OPERATION IS UNSUCCESSFUL

    def add_installed_app(self, app: sadb.InstalledApp):
        """
        Add app to the installed database
        """
        """
        Adds the given list of apps to the database.

        Parameters:
            apps (list): The list of apps to add.
        """
        # Prevent apps with the same package name
        self.c.execute("SELECT * FROM installed WHERE src_pkg_name=?", (app.src_pkg_name,))
        if self.c.fetchone() is not None:
            raise ValueError(f"An app with src_pkg_name {app.src_pkg_name} already exists.")
        self.c.execute("INSERT OR REPLACE INTO installed VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                app.app_id, app.name, app.primary_src, app.src_pkg_name, app.icon_url,
                app.author, app.summary, app.description, tcsl(app.categories),
                tcsl(app.keywords), tcsl(app.mimetypes), app.app_license, app.pricing.value,
                app.mobile.value, app.still_rating.value, app.still_rating_notes, app.homepage,
                app.donate_url, tcsl(app.screenshot_urls), app.demo_url, tcsl(app.addons), app.update_available
            )
        )
        self.conn.commit()

    def add_installed_apps(self, apps: List[sadb.InstalledApp]):
        """
        Add app to the installed database.

        Parameters:
            app (sadb.InstalledApp): The app to add.
        """
        self.c.execute("SELECT src_pkg_name FROM installed")
        existing_pkgs = [row[3] for row in self.c.fetchall()]
        apps = remove_duplicate_apps(apps)
        apps_data = [
            (
                app.app_id, app.name, app.primary_src, app.src_pkg_name, app.icon_url,
                app.author, app.summary, app.description, tcsl(app.categories),
                tcsl(app.keywords), tcsl(app.mimetypes), app.app_license, app.pricing.value,
                app.mobile.value, app.still_rating.value, app.still_rating_notes, app.homepage,
                app.donate_url, tcsl(app.screenshot_urls), app.demo_url, tcsl(app.addons), app.update_available
            ) for app in apps if app.src_pkg_name not in existing_pkgs
        ]
        self.c.executemany("INSERT OR REPLACE INTO installed VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", apps_data)
        self.conn.commit()


def get_readable_db() -> ReadableDB:
    return ReadableDB(SadbConfig())
