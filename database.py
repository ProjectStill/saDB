from typing import List

import sqlite3
import sadb_classes as sadb
import os.path
from urllib.parse import urlparse, urlunparse

PATH = os.path.join(os.path.dirname(__file__), 'sadb.db')

# Shortened alias functions
tcsl = sadb.to_csl
fcsl = sadb.from_csl

# Read-only version of the database
class ReadableDB:
    def __init__(self):
        # Use uri workaround to open in read-only mode
        file_uri = urlunparse(urlparse(PATH)._replace(scheme='file')) + "?mode=ro"
        self.conn = sqlite3.connect(file_uri, uri=True)
        self.c = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.conn.close()

    def get_app(self, app_id: str) -> sadb.App:
        self.c.execute("SELECT * FROM apps WHERE id=?", (app_id))
        app = self.c.fetchone()
        return sadb.App(*app)
    
    @staticmethod
    def column_to_app(column: tuple):
        # make sure the column length is equal ot what it should be
        assert len(column) == 23
        return App(
            column[0],
            
        )

    def get_all_apps(self) -> list:
        self.c.execute("SELECT * FROM apps")
        return [sadb.App(*app) for app in self.c.fetchall()]


class WritableDB(ReadableDB):
    def __init__(self):
        self.conn = sqlite3.connect(PATH)
        self.c = self.conn.cursor()

    def create_db(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS apps
            (id text, name text, primary_src text, src_pkg_name text, icon_url text, 
            author text, summary text, description text, categories text, keywords text, 
            mimetypes text, license text, pricing text, mobile text, still_rating text, 
            still_rating_notes text, homepage text, donate_url text, screenshot_urls text, 
            demo_url text, addons text)''')


    def add_app_to_db(self, app: sadb.App) -> None:
        self.c.execute("INSERT INTO apps VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
            (
                app.id, app.name, app.primary_src, app.src_pkg_name, app.icon_url, 
                app.author, app.summary, app.description, tcsl(app.categories),
                tcsl(app.keywords), tcsl(app.mimetypes), app.app_license, app.pricing.name,
                app.mobile.name, app.still_rating.name, app.still_rating_notes, app.homepage,
                app.donate_url, tcsl(app.screenshot_urls), app.demo_url, tcsl(app.addons)
            )
        )
        self.conn.commit()


    def add_apps_from_db(self, apps: List[sadb.App]) -> None:
        # Generated data
        apps_data = [
            (
                app.id, app.name, app.primary_src, app.src_pkg_name, app.icon_url, 
                app.author, app.summary, app.description, tcsl(app.categories),
                tcsl(app.keywords), tcsl(app.mimetypes), app.app_license, app.pricing.name,
                app.mobile.name, app.still_rating.name, app.still_rating_notes, app.homepage,
                app.donate_url, tcsl(app.screenshot_urls), app.demo_url, tcsl(app.addons)
            ) for app in apps
        ]
        self.c.executemany("INSERT INTO apps VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", apps_data)
        self.conn.commit()