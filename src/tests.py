import os
import shutil
import unittest
import tempfile

import yaml

import source_man
import yaml_parse as yp
import sadb_classes as sadb
import database as db
import configuration as cfg

config = cfg.SadbConfig()
config.db_location = "test/test.db"  # change the path to prevent overwriting the real database
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
        self.write_db = db.WritableDB(config)
        self.write_db.create_db()
        self.read_db = db.ReadableDB(config)
        test_app = sadb.App(
            "test-app", "Test App", "flathub", "test-app",
            "https://example.com/icon.png","John Doe", "A test app",
            "This is a test app", ["Test", "App"], ["test", "app"],["test/app"],
            "MIT", sadb.Pricing.FREE, sadb.MobileType.UNKNOWN, sadb.StillRating.UNKNOWN,
            "This is a test app","https://example.com","https://example.com/donate",
            ["https://example.com/screenshot1.png", "https://example.com/screenshot2.png"],
            "https://example.com/demo", ["addon1", "addon2"]
        )

    def test_clear_db(self):
        self.write_db.add_app(test_app)
        self.write_db.clear_db()
        self.write_db.conn.commit()
        self.assertEqual(self.read_db.get_all_apps(), [])

    def test_create_db(self):
        if os.path.isfile(db.PATH):
            os.remove(db.PATH)
        self.write_db.create_db()
        self.assertTrue(db.is_valid_sqlite_db())

    def test_database_exists(self): # test if the database file exists
        self.assertTrue(os.path.exists(db.PATH))

    def test_add_app_and_get_app(self):
        self.write_db.clear_db()
        self.write_db.add_app(test_app)
        app = self.read_db.get_app("test-app")
        self.assertIsInstance(app, sadb.App)
        self.assertEqual(app.app_id, "test-app")

    def test_add_app_and_get_from_query(self):
        self.write_db.clear_db()
        self.write_db.add_app(test_app)
        app = self.read_db.get_apps_from_query("SELECT * FROM apps WHERE id='test-app'")
        self.assertIsInstance(app, list)
        self.assertIsInstance(app[0], sadb.App)
        self.assertEqual(app[0].app_id, "test-app")

    def test_add_apps_and_get_all(self):
        self.write_db.clear_db()

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


class TestSourceMan(unittest.TestCase):
    source_yaml = """flathub:
  source_type: flatpak
  title: Flathub
  repo_url: https://dl.flathub.org/repo/
  homepage: https://flathub.org/
  description: Flathub is a repository of Flatpak applications.
  comment: Flathub is a repository of Flatpak applications.
  icon_url: https://dl.flathub.org/repo/logo.svg
  gpg: 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
  alt_urls: # Can be used for mirrors
    - https://front-ams.flathub.org/repo
    - https://front-hex2.flathub.org/repo
snap:  # Snap supported coming soon
  source_type: snap
  title: Snap"""

    def test_source_generation(self):
        if os.path.exists("sources"):
            shutil.rmtree("sources")
        os.mkdir("sources")
        source_man.generate_sources(self.source_yaml, testing=True)
        # Check if the sources match expected

        # MAKE SURE TO UPDATE THIS WHEN YOU ADD MORE SOURCES
        # Flatpak
        with open("sources/flathub/flathub.repo", "r") as file:
            flathub = file.read()

        # Makes sure the test yaml for flatpak is the same as the flatpak repo that should be generated
        # The .replace is used to workaround python formatting the string differently for the sake of testing
        self.assertEqual(flathub.replace("\n", ""), """[Flatpak Repo]
title = flathub
url = https://dl.flathub.org/repo/
homepage = https://flathub.org/
description = Flathub is a repository of Flatpak applications.
comment = https://dl.flathub.org/repo/logo.svg
icon = https://dl.flathub.org/repo/logo.svg
gpgkey = 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
""".replace("\n", ""))


    # MAKE SURE TO UPDATE THIS WHEN YOU ADD MORE SOURCES
    def test_flatpak_checking(self):
        if os.path.exists("sources"):
            shutil.rmtree("sources")
        os.makedirs("sources")

        source = source_man.FlatpakType(self.source_yaml, "flathub")
        source.config_folder = "sources/"

        # Create invalid file
        with open("sources/flathub.repo", "w") as file:
            file.write("Invalid file")
        self.assertEqual(source.check_config()[1], "Error parsing config file for $")

        # Test missing "[Flatpak Repo]"
        with open("sources/flathub.repo", "w") as file:
            file.write("[Thickpak Repo]/ntitle = flathub")
        self.assertEqual(source.check_config()[1], "No Flatpak Repo section in $")

        # Test url difference
        with open("sources/flathub.repo", "w") as file:
            file.write("""[Flatpak Repo]
title = flathub
url = https://dl.thickhub.org/repo/
homepage = https://flathub.org/
description = Flathub is a repository of Flatpak applications.
comment = https://dl.flathub.org/repo/logo.svg
icon = https://dl.flathub.org/repo/logo.svg
gpgkey = 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
""")
        self.assertEqual(source.check_config()[1], "Repo URL does not match for $")

        # Test to make sure alternative URLs still pass
        with open("sources/flathub.repo", "w") as file:
            file.write("""[Flatpak Repo]
title = flathub
url = https://front-hex2.flathub.org/repo
homepage = https://flathub.org/
description = Flathub is a repository of Flatpak applications.
comment = https://dl.flathub.org/repo/logo.svg
icon = https://dl.flathub.org/repo/logo.svg
gpgkey = mQINBFlD2sABEADsiUZUOYBg1UdDaWkEdJYkTSZD68214m8Q1fbrP5AptaUfCl8KYKFMNoAJRBXn9FbE6q6VBzghHXj/rSnA8WPnkbaEWR7xltOqzB1yHpCQ1l8xSfH5N02DMUBSRtD/rOYsBKbaJcOgW0K21sX+BecMY/AI2yADvCJEjhVKrjR9yfRX+NQEhDcbXUFRGt9ZT+TI5yT4xcwbvvTu7aFUR/dH7+wjrQ7lzoGlZGFFrQXSs2WI0WaYHWDeCwymtohXryF8lcWQkhH8UhfNJVBJFgCY8Q6UHkZG0FxMu8xnIDBMjBmSZKwKQn0nwzwM2afskZEnmNPYDI8nuNsSZBZSAw+ThhkdCZHZZRwzmjzyRuLLVFpOj3XryXwZcSefNMPDkZAuWWzPYjxS80cm2hG1WfqrG0Gl8+iX69cbQchb7gbEb0RtqNskTo9DDmO0bNKNnMbzmIJ3/rTbSahKSwtewklqSP/01o0WKZiy+n/RAkUKOFBprjJtWOZkc8SPXV/rnoS2dWsJWQZhuPPtv3tefdDiEyp7ePrfgfKxuHpZES0IZRiFI4J/nAUP5bix+srcIxOVqAam68CbAlPvWTivRUMRVbKjJiGXIOJ78wAMjqPg3QIC0GQ0EPAWwAOzzpdgbnG7TCQetaVV8rSYCuirlPYN+bJIwBtkOC9SWLoPMVZTwQARAQABtC5GbGF0aHViIFJlcG8gU2lnbmluZyBLZXkgPGZsYXRodWJAZmxhdGh1Yi5vcmc+iQJUBBMBCAA+FiEEblwF2XnHba+TwIE1QYTdTZB6fK4FAllD2sACGwMFCRLMAwAFCwkIBwIGFQgJCgsCBBYCAwECHgECF4AACgkQQYTdTZB6fK5RJQ/+Ptd4sWxaiAW91FFk7+wmYOkEe1NY2UDNJjEEz34PNP/1RoxveHDt43kYJQ23OWaPJuZAbu+fWtjRYcMBzOsMCaFcRSHFiDIC9aTp4ux/mo+IEeyarYt/oyKb5t5lta6xaAqg7rwt65jW5/aQjnS4h7eFZ+dAKta7Y/fljNrOznUp81/SMcx4QA5G2Pw0hs4Xrxg59oONOTFGBgA6FF8WQghrpR7SnEe0FSEOVsAjwQ13Cfkfa7b70omXSWp7GWfUzgBKyoWxKTqzMN3RQHjjhPJcsQnrqH5enUu4Pcb2LcMFpzimHnUgb9ft72DP5wxfzHGAWOUiUXHbAekfq5iFks8cha/RST6wkxG3Rf44Zn09aOxh1btMcGL+5xb1G0BuCQnA0fP/kDYIPwh9z22EqwRQOspIcvGeLVkFeIfubxpcMdOfQqQnZtHMCabV5Q/Rk9K1ZGc8M2hlg8gHbXMFch2xJ0Wu72eXbA/UY5MskEeBgawTQnQOK/vNm7t0AJMpWK26Qg6178UmRghmeZDj9uNRc3EI1nSbgvmGlpDmCxaAGqaGL1zW4KPW5yN25/qeqXcgCvUjZLI9PNq3Kvizp1lUrbx7heRiSoazCucvHQ1VHUzcPVLUKKTkoTP8okThnRRRsBcZ1+jI4yMWIDLOCT7IW3FePr+3xyuy5eEo9a25Ag0EWUPa7AEQALT/CmSyZ8LWlRYQZKYw417p7Z2hxqd6TjwkwM3IQ1irumkWcTZBZIbBgrSOg6CcXD2oWydCQHWi9qaxhuhEl2bJL5LskmBcMxVdQeD0LLHd8QUnbnnIby8ocvWN1alPfvJFjCUTrmD22U1ycOzRw2lIe4kiQONbOZtdWrVImQQSndjFlisitbmlWHvHm2lOOYy8+GJB7YffVV193hmnBSJffCy4bvkuLxsI+n1DhOzc7MPV3z6HGk4HiEcF0yyt9tCYhpsxHFdBoq2h771HfAcS0s98EVAqYMFnf9em+4cnYpdI6mhIfS1FQiKl6DBAYA8tT3ggla00DurPo0JwX/zN+PaO5h/6O9aCZwV7G6rbkgMuqMergXaf8oP38gr0z+MqWnkfM63Bodq68GP4l4hd02BoFBbDf38TMuGQB14+twJMdfbAxo2MbgluvQgfwHfZ2ca6gyEY+9s/YD1gugLjV+S6CB51WkFNe1z4tAPgJZNxUcKCbeaHNbthl8Hks/pY9RCEseX/EdfzF18epbSjJMPh4DPQXbUoFwmyuYcoBOPmvZHNl9hK7B/1RP8w1ZrXk8qdupC0SNbafX7270B7lMMVImzZetGsM9ypXJ6llhp3FwW09iseNyGJGPsr/dvTMGDXqOPfU/9SAS1LSTY4K9PbRtdrBE318YX8mIk5ABEBAAGJBHIEGAEIACYWIQRuXAXZecdtr5PAgTVBhN1NkHp8rgUCWUPa7AIbAgUJEswDAAJACRBBhN1NkHp8rsF0IAQZAQgAHRYhBFSmzd2JGfsgQgDYrFYnAunj7X7oBQJZQ9rsAAoJEFYnAunj7X7oR6AP/0KYmiAFeqx14Z43/6s2gt3VhxlSd8bmcVV7oJFbMhdHBIeWBp2BvsUf00I0Zl14ZkwCKfLwbbORC2eIxvzJ+QWjGfPhDmS4XUSmhlXxWnYEveSek5Tde+fmu6lqKM8CHg5BNx4GWIX/vdLi1wWJZyhrUwwICAxkuhKxuP2Z1An48930eslTD2GGcjByc27+9cIZjHKa07I/aLffo04V+oMT9/tgzoquzgpVV4jwekADo2MJjhkkPveSNI420bgT+Q7Fi1l0X1aFUniBvQMsaBa27PngWm6xE2ZYvh7nWCdd5g0c0eLIHxWwzV1lZ4Ryx4ITO/VL25ItECcjhTRdYa64sA62MYSaB0x3eR+SihpgP3wSNPFu3MJo6FKTFdi4CBAEmpWHFW7FcRmd+cQXeFrHLN3iNVWryy0HK/CUEJmiZEmpNiXecl4vPIIuyF0zgSCztQtKoMr+injpmQGC/rF/ELBVZTUSLNB350S0Ztvw0FKWDAJSxFmoxt3xycqvvt47rxTrhi78nkk6jATKGyvP55sO+K7Q7Wh0DXA69hvPrYW2eu8jGCdVGxi6HX7L1qcfEd0378S71dZ3g9o6KKl1OsDWWQ6MJ6FGBZedl/ibRfs8p5+sbCX3lQSjEFy3rx6n0rUrXx8U2qb+RCLzJlmC5MNBOTDJwHPcX6gKsUcXZrEQALmRHoo3SrewO41RCr+5nUlqiqV3AohBMhnQbGzyHf2+drutIaoh7Rj80XRh2bkkuPLwlNPf+bTXwNVGse4bej7B3oV6Ae1N7lTNVF4Qh+1OowtGjmfJPWo0z1s6HFJVxoIof9z58Msvgao0zrKGqaMWaNQ6LUeC9g9Aj/9Uqjbo8X54aLiYs8Z1WNc06jKP+gv8AWLtv6CR+l2kLez1YMDucjm7v6iuCMVAmZdmxhg5I/X2+OM3vBsqPDdQpr2TPDLX3rCrSBiS0gOQ6DwN5N5QeTkxmY/7QO8bgLo/Wzu1iilH4vMKW6LBKCaRx5UEJxKpL4wkgITsYKneIt3NTHo5EOuaYk+y2+Dvt6EQFiuMsdbfUjs3seIHsghX/cbPJa4YUqZAL8C4OtVHaijwGo0ymt9MWvS9yNKMyT0JhN2/BdeOVWrHk7wXXJn/ZjpXilicXKPx4udCF76meE+6N2u/T+RYZ7fP1QMEtNZNmYDOfA6sViuPDfQSHLNbauJBo/n1sRYAsL5mcG22UDchJrlKvmK3EOADCQg+myrm8006LltubNB4wWNzHDJ0Ls2JGzQZCd/xGyVmUiidCBUrD537WdknOYE4FD7P0cHaM9brKJ/M8LkEH0zUlo73bY4XagbnCqve6PvQb5G2Z55qhWphd6f4B6DGed86zJEa/RhS
""")
        self.assertTrue(source.check_config()[0])