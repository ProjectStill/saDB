import yaml
from typing import List
from sadb import App


def get_apps_from_yaml_path(path: str) -> List[App]:
    """
    Function to get apps from a YAML file.

    Args:
        path (str): The path of the YAML file.

    Returns:
        List[App]: A list of apps.
    """
    with open(path, 'r') as file:
        return get_apps_from_yaml(file.read())


def get_apps_from_yaml(yml: str) -> List[App]:
    """
    Function to get apps from a YAML string.

    Args:
        yml (str): The YAML string.

    Returns:
        List[App]: A list of apps.
    """
    apps = yaml.safe_load(yml)

    app_list = []
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
    """
    Function to convert an app to a YAML string.

    Args:
        app (App): The app.

    Returns:
        str: The YAML string.
    """
    app_dict = {app.app_id: {
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
        "pricing": app.pricing.value,
        "mobile": app.mobile.value,
        "still_rating": app.still_rating.value,
        "still_rating_notes": app.still_rating_notes,
        "homepage": app.homepage,
        "donate_url": app.donate_url,
        "screenshot_urls": app.screenshot_urls,
        "demo_url": app.demo_url,
        "addons": app.addons
    }}
    return yaml.dump(app_dict, sort_keys=False)
