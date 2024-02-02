import yaml
from typing import List
from sadb_classes import App
from __main__ import *

PATH = 'test.yaml'

def get_apps_from_yaml(path) -> List[App]:
    with open(PATH, 'r') as f:
        app_list = []
        apps = yaml.safe_load(f)
        # create item for each key with the values being used in the app

        for key, value in apps.items():
            app = App(
                key, value.get("name", None), value.get("primary_src", None), 
                value.get("src_pkg_name", None), value.get("icon_url", None), 
                value.get("author", None), value.get("summary", None), 
                value.get("description", None), value.get("categories", None), 
                value.get("keywords", None), value.get("mimetypes", None), 
                value.get("license", None), value.get("pricing", None), 
                value.get("mobile", None), value.get("still_rating", None), 
                value.get("still_rating_notes", None), value.get("homepage", None), 
                value.get("donate_url", None), value.get("screenshot_urls", None),
                value.get("demo_url", None), value.get("addons", None)
            )
            app_list.append(app)
    return app_list

def app_to_yaml(app: App) -> str:
    # app to dict
    app_dict = {app.id: {
        "name": app.name,
        "primary_src": app.primary_src,
        "src_pkg_name": app.src_pkg_name,
        "icon_url": app.icon_url,
        "author": app.author,
        "summary": app.summary,
        "description": app.description,
        "categories": app.categories,
        "keywords": app.keywords,
        "mimetypes": app.mimetypes,
        "license": app.app_license,
        "pricing": app.pricing.name,
        "mobile": app.mobile.name,
        "still_rating": app.still_rating.name,
        "still_rating_notes": app.still_rating_notes,
        "homepage": app.homepage,
        "donate_url": app.donate_url,
        "screenshot_urls": app.screenshot_urls,
        "demo_url": app.demo_url,
        "addons": app.addons
    }}
    return yaml.dump(app_dict, sort_keys=False)