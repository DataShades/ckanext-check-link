[![Tests](https://github.com/DataShades/ckanext-check-link/workflows/Tests/badge.svg?branch=main)](https://github.com/DataShades/ckanext-check-link/actions)

# ckanext-check-link

Link checker for CKAN.

Provides API, CLI commands, and views for:

* checking availability of the file, refereed by resource
* checking availability of any arbitrary link.
* storing results of these checks
* visualizing stored results

<!-- * downloading a report based on the stored results -->

### Index

* [Requirements](#requirements)
* [Installation](#installation)
* [Config settings](#config-settings)
* [UI](#ui)
* [CLI](#cli)
* [API](#api)

## Requirements

Compatibility with core CKAN versions:

| CKAN version | Compatible? |
|--------------|-------------|
| 2.9          | yes         |
| 2.10         | yes         |

## Installation

1. Install `ckanext-check-link`
   ```
   pip install ckanext-check-link
   ```

2. Add `check_link` and `collection` to the `ckan.plugins` setting in your CKAN config file.

3. Initialize the database tables.
    ```sh
    ckan -c /path/to/your/ckan.ini db pending-migrations --apply
    ```

## Config settings

```ini
# Allow any logged-in user to check links. This implies specific security issues,
# thus disabled by default.
# (optional, default: false).
ckanext.check_link.user_can_check_url = yes

# URL for the "Link availability" page.
# (optional, default: /check-link/report/global)
ckanext.check_link.report.base_template = /ckan-admin/link-state

# A base template that is extended by the "Link availability" page.
# (optional, default: check_link/base_admin.html)
ckanext.check_link.report.base_template = check_link/base.html

```

## UI

### Link availability
#### Endpoint: `check_link.report`
#### Path: `/check-link/report/global`

Paginated listing of all the "broken" links. Access is controlled by the
`check_link_view_report_page` auth function, which can be bypassed only by
sysadmin.

## CLI

CLI commands are registered under `ckan check-link` route.


### `check-packages`

Check every resource inside each package.

The scope can be narrowed via arbitrary number of arguments, specifying the package's ID or name.

```sh
# check all the public packages
$ ckan check-link check-packages

# check all the active packages
$ ckan check-link check-packages --include-private

# check all the public and draft pacakges
$ ckan check-link check-packages --include-draft

# check only two specified packages
$ ckan check-link check-packages pkg-id-one pkg-name-two

```

### `check-resources`
Check every resource on the portal.

Scope can be narrowed via arbitary number of arguments, specifying resource's ID

### `delete-reports`
Delete check-link reports.

```sh
# delete all reports
$ ckan check-link delete-reports

# drop reports that point to an unexisting resource
$ ckan check-link delete-reports --orphans-only
```

Scope can be narrowed via arbitary number of arguments, specifying resource's ID

## API

### `check_link_url_check`
### `check_link_resource_check`
### `check_link_package_check`
### `check_link_organization_check`
### `check_link_group_check`
### `check_link_user_check`
### `check_link_search_check`

### `check_link_report_save`
### `check_link_report_show`
### `check_link_report_search`
### `check_link_report_delete`

TBA

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
