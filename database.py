from typing import List

import sqlite3
import sadb_classes as sadb
from configuration import SadbConfig
import os.path
from urllib.parse import urlparse, urlunparse

PATH = os.path.join(os.path.dirname(__file__), 'sadb.db')

# Shortened alias functions
tcsl = sadb.to_csl
fcsl = sadb.from_csl


# Checks if the database is the correct format
def is_valid_sqlite_db() -> bool:
    out = True
    conn = None
    try:
        conn = sqlite3.connect(PATH)
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
    def __init__(self, config: SadbConfig, init_db: bool = True):
        if init_db:  # used to prevent init of the connection for writable db
            # Use uri workaround to open in read-only mode
            file_uri = urlunparse(urlparse(os.path.abspath(config.db_location))._replace(scheme='file')) + "?mode=ro"
            self.conn = sqlite3.connect(file_uri, uri=True)
            self.c = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.conn.close()

    def get_app(self, app_id: str) -> sadb.App:
        self.c.execute("SELECT * FROM apps WHERE id=?", (app_id, ))
        app = self.c.fetchone()
        return sadb.App(*app)

    # Converts a sql query to an App class
    @staticmethod
    def column_to_app(column: tuple):
        # make sure the column length is equal to what it should be
        assert len(column) == 21
        return sadb.App(
            column[0], column[1], column[2], column[3], column[4], column[5],
            column[6], column[7], fcsl(column[8]), fcsl(column[9]), fcsl(column[10]),
            column[11], sadb.Pricing(column[12]), sadb.MobileType((column[13])),
            sadb.StillRating(column[14]), column[15], column[16], column[17], fcsl(column[18]),
            column[19], fcsl(column[20])
        )

    def get_all_apps(self) -> list:
        self.c.execute("SELECT * FROM apps")
        return [self.column_to_app(app) for app in self.c.fetchall()]

    def get_apps_from_query(self, query: str) -> list:
        self.c.execute(query)
        return [self.column_to_app(app) for app in self.c.fetchall()]


class WritableDB(ReadableDB):
    def __init__(self, config: SadbConfig):
        new_db = not os.path.exists(config.db_location)
        # Create folders for database if they don't exist
        if new_db and not os.path.exists(os.path.dirname(config.db_location)):
            os.makedirs(os.path.dirname(config.db_location), exist_ok=True)

        self.conn = sqlite3.connect(config.db_location)
        self.c = self.conn.cursor()
        if new_db:
            self.create_db()
        super().__init__(config, init_db=False)

    def create_db(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS apps
            (id text, name text, primary_src text, src_pkg_name text, icon_url text, 
            author text, summary text, description text, categories text, keywords text, 
            mimetypes text, license text, pricing int, mobile int, still_rating int, 
            still_rating_notes text, homepage text, donate_url text, screenshot_urls text, 
            demo_url text, addons text)''')

    def add_app(self, app: sadb.App) -> None:
        # Prevent apps with the same package name
        self.c.execute("SELECT * FROM apps WHERE src_pkg_name=?", (app.src_pkg_name,))
        if self.c.fetchone() is not None:
            raise ValueError(f"An app with src_pkg_name {app.src_pkg_name} already exists.")
        self.c.execute("INSERT INTO apps VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
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
        # Generated data
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
        self.c.executemany("INSERT INTO apps VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", apps_data)
        self.conn.commit()

    def clear_db(self) -> None:
        self.c.execute("DELETE FROM apps")
        #  self.conn.commit()  REMOVE COMMIT INCASE FUTURE OPERATION IS UNSECCESSFUL