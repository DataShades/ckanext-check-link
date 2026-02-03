# ckanext-check-link

[![Tests](https://github.com/DataShades/ckanext-check-link/workflows/Tests/badge.svg?branch=main)](https://github.com/DataShades/ckanext-check-link/actions)

## Link Checker Extension for CKAN

**ckanext-check-link** is a comprehensive link checking extension for CKAN that
provides robust functionality for monitoring and managing the availability of
resources and external links within your CKAN data portal. The extension offers
API endpoints, CLI commands, and administrative UI components to help maintain
data quality and ensure that resources remain accessible to users.

### Table of Contents

* [Goals and Objectives](#goals-and-objectives)
* [Use Cases](#use-cases)
* [Features](#features)
* [Requirements](#requirements)
* [Installation](#installation)
* [Configuration](#configuration)
* [User Interface](#user-interface)
* [Command Line Interface](#command-line-interface)
* [API Documentation](#api-documentation)
* [Future Plans](#future-plans)
* [License](#license)

## Goals and Objectives

The primary goals of **ckanext-check-link** are:

1. **Maintain Data Quality**: Automatically monitor and report on broken links and unavailable resources to maintain high data quality standards.
2. **Improve User Experience**: Prevent users from encountering dead links and inaccessible resources by identifying issues proactively.
3. **Administrative Oversight**: Provide administrators with comprehensive reporting and management tools for link health monitoring.
4. **Scalable Monitoring**: Support bulk checking of resources across packages, organizations, groups, and users with configurable parameters.
5. **Flexible Integration**: Offer multiple interfaces (API, CLI, UI) to accommodate different operational workflows and automation needs.

## Use Cases

### Data Portal Administrators
- Regular monitoring of all resources in the portal to identify broken links
- Generating reports for stakeholders on data availability
- Bulk checking of resources after system updates or migrations
- Managing orphaned reports and cleaning up old records

### Data Publishers
- Checking individual resources before publishing to ensure accessibility
- Verifying that uploaded files and external links are working properly
- Monitoring the health of their published datasets over time

### System Integrators
- Automating link checking through scheduled jobs using CLI commands
- Integrating link checking into CI/CD pipelines for data quality assurance
- Building custom dashboards and notifications based on check results
- Implementing automated cleanup of outdated reports

### Data Consumers
- Receiving assurance that linked resources are accessible
- Reduced frustration from encountering broken links
- Improved trust in the data portal's reliability

## Features

### Core Functionality
- **URL Availability Checking**: Verify the accessibility of any URL, including resource URLs and arbitrary links
- **Resource-Level Checking**: Check individual CKAN resources for availability
- **Package-Level Checking**: Check all resources within specific packages
- **Organization/Group/User Checking**: Bulk check resources associated with organizations, groups, or users
- **Search-Based Checking**: Perform link checks based on complex search queries
- **Report Storage**: Store check results with detailed metadata for historical tracking
- **Report Visualization**: Administrative UI for viewing and managing link check reports

### Advanced Features
- **Configurable Timeouts**: Set custom timeout values for HTTP requests
- **Rate Limiting**: Configure delays between requests to avoid overwhelming target servers
- **Bulk Processing**: Process large numbers of resources in configurable chunks
- **Orphan Report Management**: Identify and remove reports for deleted or inactive resources
- **Cascade Deletion**: Optionally remove reports when associated resources are deleted
- **CSV Export**: Export link check reports in CSV format for external analysis

## Requirements

### Compatibility
This extension is compatible with the following CKAN versions:

| CKAN Version | Compatible |
|--------------|------------|
| 2.9          | No         |
| 2.10         | Yes        |
| 2.11         | Yes        |
| master       | Yes        |

### Dependencies
- Python 3.10+
- CKAN v2.10 or newer
- `check-link` library (~0.0.10)
- `typing-extensions`
- `ckanext-toolbelt`

## Installation

### Using pip
1. Activate your CKAN virtual environment:
   ```bash
   . /path/to/ckan/bin/activate
   ```

2. Install the extension:
   ```bash
   pip install ckanext-check-link
   ```

3. Add the `check_link` plugin to your CKAN configuration file (usually `production.ini` or `development.ini`):
   ```ini
   ckan.plugins = ... check_link ...
   ```

4. Initialize the database tables:
   ```bash
   ckan db upgrade -p check_link
   ```

5. Restart your CKAN server.

### From Source
1. Clone the repository:
   ```bash
   git clone https://github.com/DataShades/ckanext-check-link.git
   cd ckanext-check-link
   ```

2. Install in development mode:
   ```bash
   pip install -e .
   ```

3. Follow steps 3-5 from the pip installation method above.

## Configuration

The extension supports several configuration options that can be added to your CKAN configuration file:

### Basic Configuration
```ini
# Allow any logged-in user to check links. This implies specific security considerations,
# thus disabled by default.
# (optional, default: false)
ckanext.check_link.user_can_check_url = false

# Enable showing header link in the UI
# (optional, default: false)
ckanext.check_link.show_header_link = false

# Timeout for link checking requests (in seconds)
# (optional, default: 10)
ckanext.check_link.check.timeout = 10

# Enable automatic removal of reports when resources are deleted
# (optional, default: false)
ckanext.check_link.remove_reports_when_resource_deleted = false
```

### Report UI Configuration
```ini
# URL for the "Link availability" page
# (optional, default: /check-link/report/global)
ckanext.check_link.report.url = /check-link/report/global

# A base template that is extended by the "Link availability" page
# (optional, default: check_link/base_admin.html)
ckanext.check_link.report.base_template = check_link/base_admin.html
```

## User Interface

### Link Availability Report
The extension provides an administrative interface for viewing link check reports.

**Endpoint**: `check_link.report`
**Path**: `/check-link/report/global` (configurable)

**Description**: Paginated listing of all "broken" links. Access is controlled by the `check_link_view_report_page` authorization function, which is restricted to sysadmin users by default.

**Features**:
- Pagination with 10 items per page
- CSV export functionality
- Detailed information about broken links including:
  - Data record title
  - Data resource title
  - Organization
  - State (available, broken, etc.)
  - Error type
  - Link to data resource
  - Date and time checked

## Command Line Interface

CLI commands are registered under the `ckan check-link` route and provide powerful tools for bulk operations and automation.

### `check-packages`

Check every resource inside each package. The scope can be narrowed via arbitrary number of arguments, specifying the package's ID or name.

**Usage**:
```bash
# Check all the public packages
ckan check-link check-packages

# Check all the active packages (includes private)
ckan check-link check-packages --include-private

# Check all the public and draft packages
ckan check-link check-packages --include-draft

# Check only two specified packages
ckan check-link check-packages pkg-id-one pkg-name-two

# Process packages in chunks of 10 with 0.5 second delay between requests
ckan check-link check-packages --chunk 10 --delay 0.5

# Set custom timeout for requests (20 seconds)
ckan check-link check-packages --timeout 20
```

**Options**:
- `-d, --include-draft`: Check draft packages as well
- `-p, --include-private`: Check private packages as well
- `-c, --chunk INTEGER`: Number of packages processed simultaneously (default: 1)
- `-d, --delay FLOAT`: Delay between requests in seconds (default: 0)
- `-t, --timeout FLOAT`: Request timeout in seconds (default: 10)
- `IDS`: Package IDs or names to check (optional, checks all if none provided)

### `check-resources`

Check every resource on the portal. Scope can be narrowed via arbitrary number of arguments, specifying resource's ID.

**Usage**:
```bash
# Check all active resources
ckan check-link check-resources

# Check specific resources by ID
ckan check-link check-resources resource-id-one resource-id-two

# Add delay between requests and set custom timeout
ckan check-link check-resources --delay 0.1 --timeout 15
```

**Options**:
- `-d, --delay FLOAT`: Delay between requests in seconds (default: 0)
- `-t, --timeout FLOAT`: Request timeout in seconds (default: 10)
- `IDS`: Resource IDs to check (optional, checks all if none provided)

### `delete-reports`

Delete check-link reports with optional filtering capabilities.

**Usage**:
```bash
# Delete all reports
ckan check-link delete-reports

# Drop reports that point to non-existing resources
ckan check-link delete-reports --orphans-only
```

**Options**:
- `-o, --orphans-only`: Only drop reports that point to non-existing resources

## API Documentation

The extension provides a comprehensive set of API actions for programmatic access to link checking functionality.

### Check Actions

#### `check_link_url_check`
Check the availability of one or more URLs.

**Parameters**:
- `url` (list/string, required): URL(s) to check
- `save` (boolean, optional, default: false): Save results to database
- `clear_available` (boolean, optional, default: false): Remove available reports when saving
- `skip_invalid` (boolean, optional, default: false): Skip invalid URLs instead of raising error
- `link_patch` (dict, optional, default: {}): Additional parameters for link checking (e.g., timeout, delay)

**Returns**: List of dictionaries containing check results with keys: `url`, `state`, `code`, `reason`, `explanation`

**Authorization**: Controlled by `check_link_url_check` auth function

#### `check_link_resource_check`
Check the availability of a specific resource.

**Parameters**:
- `id` (string, required): Resource ID to check
- `save` (boolean, optional, default: false): Save results to database
- `clear_available` (boolean, optional, default: false): Remove available reports when saving
- `link_patch` (dict, optional, default: {}): Additional parameters for link checking

**Returns**: Dictionary containing check result with resource metadata

**Authorization**: Requires permission to view the resource

#### `check_link_package_check`
Check all resources within a specific package.

**Parameters**:
- `id` (string, required): Package ID or name to check
- `save` (boolean, optional, default: false): Save results to database
- `clear_available` (boolean, optional, default: false): Remove available reports when saving
- `skip_invalid` (boolean, optional, default: false): Skip invalid URLs
- `include_drafts` (boolean, optional, default: false): Include draft resources
- `include_private` (boolean, optional, default: false): Include private resources
- `link_patch` (dict, optional, default: {}): Additional parameters for link checking

**Returns**: List of check results for all resources in the package

**Authorization**: Requires permission to view the package

#### `check_link_organization_check`
Check all resources within a specific organization.

**Parameters**:
- `id` (string, required): Organization ID or name to check
- `save` (boolean, optional, default: false): Save results to database
- `clear_available` (boolean, optional, default: false): Remove available reports when saving
- `skip_invalid` (boolean, optional, default: false): Skip invalid URLs
- `include_drafts` (boolean, optional, default: false): Include draft resources
- `include_private` (boolean, optional, default: false): Include private resources
- `link_patch` (dict, optional, default: {}): Additional parameters for link checking

**Returns**: List of check results for all resources in the organization

**Authorization**: Requires permission to view the organization

#### `check_link_group_check`
Check all resources within a specific group.

**Parameters**:
- `id` (string, required): Group ID or name to check
- `save` (boolean, optional, default: false): Save results to database
- `clear_available` (boolean, optional, default: false): Remove available reports when saving
- `skip_invalid` (boolean, optional, default: false): Skip invalid URLs
- `include_drafts` (boolean, optional, default: false): Include draft resources
- `include_private` (boolean, optional, default: false): Include private resources
- `link_patch` (dict, optional, default: {}): Additional parameters for link checking

**Returns**: List of check results for all resources in the group

**Authorization**: Requires permission to view the group

#### `check_link_user_check`
Check all resources created by a specific user.

**Parameters**:
- `id` (string, required): User ID or name to check
- `save` (boolean, optional, default: false): Save results to database
- `clear_available` (boolean, optional, default: false): Remove available reports when saving
- `skip_invalid` (boolean, optional, default: false): Skip invalid URLs
- `include_drafts` (boolean, optional, default: false): Include draft resources
- `include_private` (boolean, optional, default: false): Include private resources
- `link_patch` (dict, optional, default: {}): Additional parameters for link checking

**Returns**: List of check results for all resources created by the user

**Authorization**: Requires permission to view the user

#### `check_link_search_check`
Check resources based on a search query.

**Parameters**:
- `fq` (string, optional, default: "*:*"): Search filter query
- `save` (boolean, optional, default: false): Save results to database
- `clear_available` (boolean, optional, default: false): Remove available reports when saving
- `skip_invalid` (boolean, optional, default: false): Skip invalid URLs
- `include_drafts` (boolean, optional, default: false): Include draft resources
- `include_private` (boolean, optional, default: false): Include private resources
- `start` (integer, optional, default: 0): Starting index for results
- `rows` (integer, optional, default: 10): Maximum number of packages to check
- `link_patch` (dict, optional, default: {}): Additional parameters for link checking

**Returns**: Dictionary with `reports` key containing list of check results

**Authorization**: Requires permission to perform package search

### Report Actions

#### `check_link_report_save`
Save a link check report to the database.

**Parameters**:
- `id` (string, optional): Report ID (auto-generated if not provided)
- `url` (string, required): URL that was checked
- `state` (string, required): State of the check (e.g., "available", "broken")
- `resource_id` (string, optional): Associated resource ID
- `details` (dict, optional, default: {}): Additional details about the check
- `package_id` (string, optional): Associated package ID

**Returns**: Dictionary representing the saved report

**Authorization**: Sysadmin only

#### `check_link_report_show`
Retrieve a specific link check report.

**Parameters**:
- `id` (string, optional): Report ID
- `resource_id` (string, optional): Resource ID to find report for
- `url` (string, optional): URL to find report for

**Note**: One of `id`, `resource_id`, or `url` must be provided.

**Returns**: Dictionary representing the report

**Authorization**: Sysadmin only

#### `check_link_report_search`
Search for link check reports with various filtering options.

**Parameters**:
- `limit` (integer, optional, default: 10): Maximum number of results to return
- `offset` (integer, optional, default: 0): Offset for pagination
- `exclude_state` (list/string, optional): States to exclude from results
- `include_state` (list/string, optional): States to include in results
- `attached_only` (boolean, optional, default: false): Only return reports attached to resources
- `free_only` (boolean, optional, default: false): Only return reports not attached to resources

**Returns**: Dictionary with `count` and `results` keys

**Authorization**: Sysadmin only

#### `check_link_report_delete`
Delete a specific link check report.

**Parameters**:
- `id` (string, optional): Report ID
- `resource_id` (string, optional): Resource ID of report to delete
- `url` (string, optional): URL of report to delete

**Note**: One of `id`, `resource_id`, or `url` must be provided.

**Returns**: Dictionary representing the deleted report

**Authorization**: Sysadmin only

## Future Plans

### Short-term Roadmap (Next 6 months)
- **Enhanced Reporting**: Add more detailed analytics and visualization options for link check results
- **Notification System**: Implement email/webhook notifications for broken links
- **Scheduled Checks**: Add built-in scheduler for automated periodic link checking
- **Performance Improvements**: Optimize bulk operations for large datasets

### Medium-term Roadmap (6-12 months)
- **Advanced Filtering**: Add more sophisticated filtering options for reports
- **API Rate Limiting**: Implement intelligent rate limiting to prevent overwhelming target servers
- **Customizable Checks**: Allow configuration of different check types (HTTP status, content validation, etc.)
- **Integration Hooks**: Add hooks for integration with external monitoring systems

### Long-term Roadmap (12+ months)
- **Machine Learning Integration**: Use ML to predict link failure patterns and suggest preventive actions
- **Multi-Protocol Support**: Extend beyond HTTP/HTTPS to support FTP, SFTP, and other protocols
- **Real-time Monitoring**: Implement real-time link monitoring with live dashboard
- **Community Features**: Add community-driven link verification and reporting

## Contributing

We welcome contributions to improve ckanext-check-link! Please see our contributing guidelines in the repository for more information on how to get involved.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers directly.

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)

This extension is licensed under the GNU Affero General Public License v3.0 or later (AGPLv3+). See the LICENSE file for more details.
