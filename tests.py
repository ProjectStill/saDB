import os
import unittest
import tempfile

import yaml

import yaml_parse as yp
import sadb_classes as sadb
import database as db

db.PATH = "test/test.db"  # change the path to prevent overwriting the real database
test_app = sadb.App(
    "test-app", "Test App", "flathub", "test-app",
    "https://example.com/icon.png","John Doe", "A test app",
    "This is a test app", ["Test", "App"], ["test", "app"],["test/app"],
    "MIT", sadb.Pricing.FREE, sadb.MobileType.UNKNOWN, sadb.StillRating.UNKNOWN,
    "This is a test app","https://example.com","https://example.com/donate",
    ["https://example.com/screenshot1.png", "https://example.com/screenshot2.png"],
    "https://example.com/demo", ["addon1", "addon2"]
)


class TestSaDBClasses(unittest.TestCase):
    def test_to_csl(self):
        self.assertEqual(sadb.to_csl(["one", "two", "three"]), "one,two,three")

    def test_from_csl(self):
        self.assertEqual(sadb.from_csl("one,two,three"), ["one", "two", "three"])


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.write_db = db.WritableDB()
        self.write_db.create_db()
        self.read_db = db.ReadableDB()
        test_app = sadb.App(
            "test-app", "Test App", "flathub", "test-app",
            "https://example.com/icon.png","John Doe", "A test app",
            "This is a test app", ["Test", "App"], ["test", "app"],["test/app"],
            "MIT", sadb.Pricing.FREE, sadb.MobileType.UNKNOWN, sadb.StillRating.UNKNOWN,
            "This is a test app","https://example.com","https://example.com/donate",
            ["https://example.com/screenshot1.png", "https://example.com/screenshot2.png"],
            "https://example.com/demo", ["addon1", "addon2"]
        )

    def clear_db(self):
        self.write_db.c.execute("DELETE FROM apps")
        self.write_db.conn.commit()

    def test_clear_db(self):
        self.write_db.add_app(test_app)
        self.clear_db()
        self.assertEqual(self.read_db.get_all_apps(), [])

    def test_create_db(self):
        if os.path.isfile(db.PATH):
            os.remove(db.PATH)
        self.write_db.create_db()
        self.assertTrue(db.is_valid_sqlite_db())

    def test_database_exists(self): # test if the database file exists
        self.assertTrue(os.path.exists(db.PATH))

    def test_add_app_and_get_app(self):
        self.clear_db()
        self.write_db.add_app(test_app)
        app = self.read_db.get_app("test-app")
        self.assertIsInstance(app, sadb.App)
        self.assertEqual(app.app_id, "test-app")

    def test_add_app_and_get_from_query(self):
        self.clear_db()
        self.write_db.add_app(test_app)
        app = self.read_db.get_apps_from_query("SELECT * FROM apps WHERE id='test-app'")
        self.assertIsInstance(app, list)
        self.assertIsInstance(app[0], sadb.App)
        self.assertEqual(app[0].app_id, "test-app")

    def test_add_apps_and_get_all(self):
        self.clear_db()

        # Create and add 3 test apps
        apps = []
        for i in range(3):
            app = sadb.App(
                f"test-app{i}", f"Test App {i}", f"https://example.com/{i}", f"test-app-{i}",
                f"https://example.com/icon{i}.png", f"John Doe", f"A test app {i}",
                f"This is a test app {i}", [f"Test{i}", f"App{i}"], [f"test{i}", f"app{i}"], [f"test/app{i}"],
                "MIT", sadb.Pricing.FREE, sadb.MobileType.UNKNOWN, sadb.StillRating.UNKNOWN,
                f"This is a test app {i}", f"https://example.com/{i}", f"https://example.com/donate{i}",
                [f"https://example.com/screenshot1{i}.png", f"https://example.com/screenshot2{i}.png"],
                f"https://example.com/demo{i}", [f"addon{i}1", f"addon{i}2"]
            )
            apps.append(app)
        self.write_db.add_apps(apps)

        read_apps = self.read_db.get_all_apps()
        self.assertIsInstance(read_apps, list)
        self.assertEqual(len(read_apps), 3)
        for app in read_apps:
            self.assertIsInstance(app, sadb.App)

    def test_column_to_app(self):
        self.assertEqual(
            self.write_db.column_to_app((
                "test-app", "Test App", "flathub", "test-app",
                "https://example.com/icon.png", "John Doe", "A test app",
                "This is a test app", "Test,App", "test,app", "test/app",
                "MIT", sadb.Pricing.FREE, sadb.MobileType.UNKNOWN, sadb.StillRating.UNKNOWN,
                "This is a test app", "https://example.com", "https://example.com/donate",
                 "https://example.com/screenshot1.png,https://example.com/screenshot2.png",
                "https://example.com/demo", "addon1,addon2"
            )).__dict__, test_app.__dict__
        )


class TestYamlParse(unittest.TestCase):
    yaml = """firefox:
  name: Firefox
  primary_src: flathub
  src_pkg_name: org.mozilla.firefox
  icon_url: https://flathub.org/repo/appstream/x86_64/icons/128x128/org.mozilla.firefox.png
  author: Mozilla
  summary: Firefox web browser
  description: |
    Firefox is a free and open-source web browser developed by the Mozilla Foundation and its subsidiary, the Mozilla Corporation.
    Firefox uses the Gecko layout engine to render web pages, which implements current and anticipated web standards.
    In 2017, Firefox began incorporating new technology under the code name Quantum to promote parallelism and a more intuitive user interface.
    An additional version, Firefox for iOS, was released on November 12, 2015.
    Due to platform restrictions, it uses the WebKit layout engine instead of Gecko, as with all other iOS web browsers.
  categories:
    - WebBrowser
  keywords:
    - web
    - browser
    - internet
    - www
    - gecko
    - mozilla
    - quantum
  mimetypes:
    - text/html
    - application/xhtml+xml
    - application/vnd.mozilla.xul+xml
    - application/vnd.mozilla.xul+xml-overlay
    - image/svg+xml
    - application/rss+xml
    - application/rdf+xml
    - application/atom+xml
    - application/x-microsumm
  license: MPL-2.0
  homepage: https://www.mozilla.org/firefox/
  donate: https://donate.mozilla.org/
  ss_urls:
    https://dl.flathub.org/repo/screenshots/org.mozilla.firefox-stable/1248x702/org.mozilla.firefox-af5d1ae7c121ea4864b3c5a1098f8f9c.png
google-chrome:
  name: Google Chrome
  primary_src: flathub
  src_pkg_name: com.google.Chrome
  icon_url: https://flathub.org/repo/appstream/x86_64/icons/128x128/com.google.Chrome.png
  author: Google
  summary: Google Chrome web browser
  description: |
    Google Chrome is a web browser developed by Google.
    It was first released in 2008 for Microsoft Windows, and was later ported to Linux, macOS, iOS, and Android.
    The browser is also the main component of Chrome OS, where it serves as the platform for web apps.
  categories:
    - WebBrowser
  keywords:
    - web
    - browser
    - internet
    - www
    - chromium
    - google
  mimetypes:
    - text/html
    - application/xhtml+xml
    - application/vnd.mozilla.xul+xml
    - application/vnd.mozilla.xul+xml-overlay
    - image/svg+xml
    - application/rss+xml
    - application/rdf+xml
    - application/atom+xml
    - application/x-microsumm
  license: Proprietary
  homepage: https://www.google.com/chrome/
  ss_urls:
    https://dl.flathub.org/repo/screenshots/com.google.Chrome-stable/1248x702/com.google.Chrome-1b9e3b5e9e0b5b9d9b9b9b9b9b9b9b9b.png
"""

    test_app_yaml = """test-app:
  name: Test App
  primary_src: flathub
  src_pkg_name: test-app
  icon_url: https://example.com/icon.png
  author: John Doe
  summary: A test app
  description: This is a test app
  categories:
    - Test
    - App
  keywords:
    - test
    - app
  mimetypes: 
    - test/app
  license: MIT
  pricing: 1
  mobile: 0
  still_rating: 0
  still_rating_notes:  This is a test app
  homepage: https://example.com
  donate_url: https://example.com/donate
  screenshot_urls:
    - https://example.com/screenshot1.png
    - https://example.com/screenshot2.png
  demo_url: https://example.com/demo
  addons:
    - addon1
    - addon2
"""

    def test_yaml_path(self):  # Tests reading yaml from a path which also tests get_apps_from_yaml
        # create a temp file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as file:
            file.write(self.yaml)
            file_path = file.name
        apps = yp.get_apps_from_yaml_path(file_path)
        self.assertIsInstance(apps, list)
        self.assertEqual(len(apps), 2)
        self.assertIsInstance(apps[0], sadb.App)
        self.assertEqual(apps[0].app_id, "firefox")
        self.assertEqual(apps[1].app_id, "google-chrome")
        os.remove(file_path)
        
    def test_app_to_yaml(self):
        self.assertEqual(yaml.safe_load(yp.app_to_yaml(test_app)), yaml.safe_load(self.test_app_yaml))
