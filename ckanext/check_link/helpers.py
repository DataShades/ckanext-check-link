from __future__ import annotations

import ckan.plugins.toolkit as tk

CONFIG_HEADER_LINK = "ckanext.check_link.show_header_link"
DEFAULT_HEADER_LINK = False


def check_link_show_header_link() -> bool:
    return tk.asbool(tk.config.get(CONFIG_HEADER_LINK, DEFAULT_HEADER_LINK))
