import copy
from xml.etree import ElementTree as etree
import gi, yaml
gi.require_version("AppStream", "1.0")
# gi.require_version("Flatpak", "1.0")
from gi.repository import AppStream, Flatpak, GLib

installation = Flatpak.Installation.new_system()
remotes_refs = installation.list_remote_refs_sync("flathub")

apps = {}

# Create an AppStream pool
pool = AppStream.Pool()

# Load system-wide metadata
pool.load()

# Get all components (applications)
components = pool.get_components()
print(components)

# id, name, primary_src, src_pkg_name, icon_url,
# author, summary, description, categories, keywords,
# mimetypes, license, pricing int, mobile int, still_rating int,
# still_rating_notes, homepage, donate_url, screenshot_urls,
# demo_url, addons

for component in components.as_array():
    if component.get_origin() == "flatpak":
        app_id = component.get_id()
        apps[app_id] = {}
        apps[app_id]["name"] = component.get_name()
        apps[app_id]["primary_src"] = "flathub"
        apps[app_id]["src_pkg_name"] = "app/" + app_id + "/x86_64/stable"
        apps[app_id]["icon_url"] = f"https://flathub.org/repo/appstream/x86_64/icons/128x128/{app_id}.png"
        apps[app_id]["summary"] = component.get_summary()
        apps[app_id]["description"] = component.get_description()
        apps[app_id]["categories"] = component.get_categories()
        apps[app_id]["keywords"] = component.get_keywords()
        #apps[app_id]["mimetypes"] = component.get_provided_for_kind(AppStream.ProvidedKind.MEDIATYPE)
        apps[app_id]["license"] = component.get_project_license()
        apps[app_id]["pricing"] = 0
        apps[app_id]["mobile"] = 0
        apps[app_id]["still_rating"] = 0
        apps[app_id]["still_rating_notes"] = ""
        apps[app_id]["homepage"] = component.get_url(AppStream.UrlKind.HOMEPAGE)
        apps[app_id]["donate_url"] = component.get_url(AppStream.UrlKind.DONATION)
        apps[app_id]["screenshot_urls"] = []
        apps[app_id]["demo_url"] = ""
        apps[app_id]["addons"] = []

        # Remove None values
        apps[app_id] = {k: v for k, v in apps[app_id].items() if v is not None}

        # Change mimetype to list
        if app_id in apps.keys():
            if apps[app_id].get("mimetypes") is not None:
                apps[app_id]["mimetypes"] = apps[app_id]["mimetypes"].get_items()


# Export dictionry to yaml
with open("apps.yaml", "w") as f:
    yaml.dump(apps, f)