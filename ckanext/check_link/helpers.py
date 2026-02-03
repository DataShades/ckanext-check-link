"""Template helper functions for the ckanext-check-link extension.

This module provides helper functions that can be used in Jinja2 templates
to customize the behavior of the link checking extension in the UI.
"""

from __future__ import annotations

import ckan.plugins.toolkit as tk

CONFIG_HEADER_LINK = "ckanext.check_link.show_header_link"
DEFAULT_HEADER_LINK = False


def check_link_show_header_link() -> bool:
    """Check if the header link should be displayed in the UI.

    This helper function checks the configuration setting to determine
    whether the link checking functionality should be accessible from
    the header navigation.

    Returns:
        True if the header link should be shown, False otherwise
    """
    return tk.asbool(tk.config.get(CONFIG_HEADER_LINK, DEFAULT_HEADER_LINK))
