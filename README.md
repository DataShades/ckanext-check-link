# ckanext-check-link

[![Tests](https://github.com/DataShades/ckanext-check-link/workflows/Tests/badge.svg?branch=main)](https://github.com/DataShades/ckanext-check-link/actions)

## Link Checker Extension for CKAN

**ckanext-check-link** is a comprehensive link checking extension for CKAN that provides robust functionality for monitoring and managing the availability of resources and external links within your CKAN data portal. The extension offers API endpoints, CLI commands, and administrative UI components to help maintain data quality and ensure that resources remain accessible to users.

This extension addresses a critical need in data portals where links to resources can become broken over time, leading to poor user experience and reduced trust in the platform. By providing automated link checking capabilities, administrators can proactively identify and address broken links before users encounter them.

## Goals and Objectives

The primary goals of **ckanext-check-link** are to maintain data quality by automatically monitoring and reporting on broken links and unavailable resources, improve user experience by preventing encounters with dead links, provide administrative oversight through comprehensive reporting tools, support scalable monitoring of resources across packages, organizations, groups, and users, and offer flexible integration through multiple interfaces including API, CLI, and UI to accommodate different operational workflows and automation needs.

The extension aims to create a more reliable data portal ecosystem where data publishers, administrators, and consumers can trust that the resources they access will be available when needed. This contributes to the overall credibility and utility of the CKAN platform.

## Use Cases

Data portal administrators regularly monitor all resources in the portal to identify broken links and generate reports for stakeholders on data availability. They perform bulk checking of resources after system updates or migrations and manage orphaned reports while cleaning up old records. This ensures that the data portal maintains high standards of accessibility and reliability.

Data publishers check individual resources before publishing to ensure accessibility and verify that uploaded files and external links are working properly. They also monitor the health of their published datasets over time, taking responsibility for maintaining the quality of their contributions to the platform.

System integrators automate link checking through scheduled jobs using CLI commands and integrate link checking into CI/CD pipelines for data quality assurance. They build custom dashboards and notifications based on check results and implement automated cleanup of outdated reports, creating seamless workflows that maintain data quality without manual intervention.

Data consumers benefit from receiving assurance that linked resources are accessible, experiencing reduced frustration from encountering broken links, and developing improved trust in the data portal's reliability. This enhanced user experience encourages continued engagement with the platform.

## Features

The core functionality of the extension includes URL availability checking to verify the accessibility of any URL, including resource URLs and arbitrary links. It provides resource-level checking for individual CKAN resources, package-level checking for all resources within specific packages, and organization/group/user checking for bulk processing of resources associated with these entities. The extension also supports search-based checking to perform link checks based on complex search queries, report storage to store check results with detailed metadata for historical tracking, and report visualization through administrative UI for viewing and managing link check reports.

Advanced features include configurable timeouts to set custom timeout values for HTTP requests, rate limiting to configure delays between requests and avoid overwhelming target servers, bulk processing to handle large numbers of resources in configurable chunks, orphan report management to identify and remove reports for deleted or inactive resources, cascade deletion to optionally remove reports when associated resources are deleted, and CSV export to export link check reports in CSV format for external analysis.

The extension also provides comprehensive API access for programmatic operations, command-line interface for bulk operations and automation, and administrative user interface for manual monitoring and management of link health.

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
- `check-link` library (~0.0.11)
- `typing-extensions`
- `ckanext-toolbelt`
- `ckanext-collection`

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

The extension provides an intuitive administrative interface for viewing and managing link check reports. The Link Availability Report page offers a paginated listing of all "broken" links with access controlled by the `check_link_view_report_page` authorization function, which is restricted to sysadmin users by default.

The interface features pagination with 10 items per page, CSV export functionality, and detailed information about broken links including data record title, data resource title, organization, state (available, broken, etc.), error type, link to data resource, and date and time checked. This comprehensive view enables administrators to quickly identify and address problematic resources.

Additionally, the extension provides organization-specific and package-specific report pages that allow for targeted monitoring of resources within specific organizational units or datasets. These views provide granular control over link monitoring activities.

## Command Line Interface

CLI commands are registered under the `ckan check-link` route and provide powerful tools for bulk operations and automation. The interface is designed to handle large-scale operations efficiently while providing real-time feedback on progress.

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

# Check packages belonging to a specific organization
ckan check-link check-packages --organization org-id-or-name
```

**Options**:
- `-d, --include-draft`: Check draft packages as well
- `-p, --include-private`: Check private packages as well
- `-c, --chunk INTEGER`: Number of packages processed simultaneously (default: 1)
- `-d, --delay FLOAT`: Delay between requests in seconds (default: 0)
- `-t, --timeout FLOAT`: Request timeout in seconds (default: 10)
- `-o, --organization TEXT`: Check packages of specific organization
- `IDS`: Package IDs or names to check (optional, checks all if none provided)

The command provides real-time progress feedback with statistics showing the distribution of link states (available, broken, etc.) as the checking progresses. This allows operators to monitor the health of their data portal in real-time during bulk operations.

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

This command is particularly useful for targeted checking of specific resources or for verifying the status of recently added or modified resources.

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

This command is essential for maintaining clean and accurate reporting data by removing obsolete reports that no longer correspond to active resources in the system.

## API Documentation

The extension provides a comprehensive set of API actions for programmatic access to link checking functionality. All API endpoints follow CKAN's standard authentication and authorization patterns, ensuring consistent security across the platform.

### Check Actions

#### `check_link_url_check`
Check the availability of one or more URLs. This action serves as the foundational building block for all other check operations in the system.

**Parameters**:
- `url` (list/string, required): URL(s) to check
- `save` (boolean, optional, default: false): Save results to database
- `clear_available` (boolean, optional, default: false): Remove available reports when saving
- `skip_invalid` (boolean, optional, default: false): Skip invalid URLs instead of raising error
- `link_patch` (dict, optional, default: {}): Additional parameters for link checking (e.g., timeout, delay)

**Returns**: List of dictionaries containing check results with keys: `url`, `state`, `code`, `reason`, `explanation`

**Authorization**: Controlled by `check_link_url_check` auth function

The state field indicates the result of the check, typically "available" for accessible URLs or "broken" for inaccessible ones. The code field contains the HTTP status code if applicable, while the reason and explanation fields provide additional diagnostic information about the check result.

#### `check_link_resource_check`
Check the availability of a specific resource. This action performs a comprehensive check of a single resource and can optionally save the results for later reference.

**Parameters**:
- `id` (string, required): Resource ID to check
- `save` (boolean, optional, default: false): Save results to database
- `clear_available` (boolean, optional, default: false): Remove available reports when saving
- `link_patch` (dict, optional, default: {}): Additional parameters for link checking

**Returns**: Dictionary containing check result with resource metadata

**Authorization**: Requires permission to view the resource

This action retrieves the resource details, extracts the URL, and performs a check using the underlying URL checking mechanism. It returns comprehensive information about both the check result and the associated resource.

#### `check_link_package_check`
Check all resources within a specific package. This action enables comprehensive checking of all resources associated with a particular dataset.

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

This action iterates through all resources in the specified package and checks each one individually, returning a comprehensive report of the status of all resources in the package.

#### `check_link_organization_check`
Check all resources within a specific organization. This action enables organization-wide link monitoring for data governance purposes.

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

This action leverages CKAN's search functionality to find all packages owned by the specified organization and then checks all resources within those packages.

#### `check_link_group_check`
Check all resources within a specific group. This action enables group-based link monitoring for thematic collections of datasets.

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

This action uses CKAN's search functionality to find all packages associated with the specified group and then checks all resources within those packages.

#### `check_link_user_check`
Check all resources created by a specific user. This action enables user-based monitoring of data contributions.

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

This action finds all packages where the specified user is the creator and then checks all resources within those packages, providing accountability for user contributions.

#### `check_link_search_check`
Check resources based on a search query. This action provides maximum flexibility for targeted link checking operations.

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

This action uses CKAN's search functionality to find packages matching the specified query and then checks all resources within those packages. The flexible query syntax allows for complex filtering criteria.

### Report Actions

#### `check_link_report_save`
Save a link check report to the database. This action manages the persistence of link check results for historical tracking and analysis.

**Parameters**:
- `id` (string, optional): Report ID (auto-generated if not provided)
- `url` (string, required): URL that was checked
- `state` (string, required): State of the check (e.g., "available", "broken")
- `resource_id` (string, optional): Associated resource ID
- `details` (dict, optional, default: {}): Additional details about the check
- `package_id` (string, optional): Associated package ID

**Returns**: Dictionary representing the saved report

**Authorization**: Sysadmin only

This action creates or updates a report record in the database. If a report already exists for the same URL and resource combination, it updates the existing record rather than creating a duplicate.

#### `check_link_report_show`
Retrieve a specific link check report. This action provides access to stored link check results.

**Parameters**:
- `id` (string, optional): Report ID
- `resource_id` (string, optional): Resource ID to find report for
- `url` (string, optional): URL to find report for

**Note**: One of `id`, `resource_id`, or `url` must be provided.

**Returns**: Dictionary representing the report

**Authorization**: Sysadmin only

This action retrieves a specific report from the database based on the provided identifier. It returns comprehensive information about the check result including timestamps and detailed diagnostics.

#### `check_link_report_search`
Search for link check reports with various filtering options. This action enables comprehensive analysis of link check history and trends.

**Parameters**:
- `limit` (integer, optional, default: 10): Maximum number of results to return
- `offset` (integer, optional, default: 0): Offset for pagination
- `exclude_state` (list/string, optional): States to exclude from results
- `include_state` (list/string, optional): States to include in results
- `attached_only` (boolean, optional, default: false): Only return reports attached to resources
- `free_only` (boolean, optional, default: false): Only return reports not attached to resources

**Returns**: Dictionary with `count` and `results` keys

**Authorization**: Sysadmin only

This action provides flexible querying capabilities for link check reports, supporting various filtering and pagination options to handle large datasets efficiently.

#### `check_link_report_delete`
Delete a specific link check report. This action enables cleanup of obsolete or erroneous reports.

**Parameters**:
- `id` (string, optional): Report ID
- `resource_id` (string, optional): Resource ID of report to delete
- `url` (string, optional): URL of report to delete

**Note**: One of `id`, `resource_id`, or `url` must be provided.

**Returns**: Dictionary representing the deleted report

**Authorization**: Sysadmin only

This action removes a specific report from the database and returns information about the deleted record for audit purposes.

## Authentication and Authorization

The extension implements comprehensive authentication and authorization controls to ensure appropriate access to link checking functionality. The authorization system follows CKAN's standard patterns and integrates seamlessly with existing permission structures.

URL checking operations can be configured to allow access to any logged-in user or restricted to administrators only through the `ckanext.check_link.user_can_check_url` configuration option. Resource, package, organization, group, and user checking operations require appropriate permissions to view the corresponding entities, leveraging CKAN's built-in authorization system.

Report management operations (save, show, search, delete) are restricted to sysadmin users to protect the integrity of the link checking data. The report viewing page authorization allows package and organization editors to view reports for their respective entities while restricting broader access to sysadmins.

## Architecture and Implementation

The extension follows CKAN's plugin architecture and implements multiple plugin interfaces to provide comprehensive functionality. The main `CheckLinkPlugin` class implements `IConfigurer` to register templates and assets, `IDomainObjectModification` to handle resource deletion events, and uses decorator patterns to register helpers, actions, CLI commands, blueprints, and auth functions.

The model layer uses SQLAlchemy to define the `Report` entity that stores link check results with relationships to CKAN's Resource and Package entities. The action layer provides the API interface with comprehensive validation schemas defined in the schema module. The CLI layer provides command-line access through Click-based commands with progress indicators and statistics.

The authentication layer implements fine-grained access controls for all operations, and the view layer provides Flask-based routes for the administrative user interface with CSV export capabilities.

## Future Plans

### Short-term Roadmap (Next 6 months)
Enhanced reporting will add more detailed analytics and visualization options for link check results, including trend analysis and predictive indicators. A notification system will implement email and webhook notifications for broken links, allowing for proactive remediation. Scheduled checks will add built-in scheduler for automated periodic link checking with configurable intervals and scopes. Performance improvements will optimize bulk operations for large datasets through improved indexing and parallel processing capabilities.

### Medium-term Roadmap (6-12 months)
Advanced filtering will add more sophisticated filtering options for reports, including date ranges, error types, and custom criteria. API rate limiting will implement intelligent rate limiting to prevent overwhelming target servers while maintaining checking efficiency. Customizable checks will allow configuration of different check types beyond basic HTTP status, including content validation and response time thresholds. Integration hooks will add hooks for integration with external monitoring systems and third-party services.

### Long-term Roadmap (12+ months)
Machine learning integration will use ML algorithms to predict link failure patterns and suggest preventive actions based on historical data. Multi-protocol support will extend beyond HTTP/HTTPS to support FTP, SFTP, and other protocols commonly used in data portals. Real-time monitoring will implement continuous link monitoring with live dashboard and alerting capabilities. Community features will add community-driven link verification and reporting mechanisms to leverage collective intelligence.

## Contributing

We welcome contributions to improve ckanext-check-link! Contributions can include bug fixes, feature enhancements, documentation improvements, and testing. Please fork the repository, create a feature branch, implement your changes with appropriate tests, and submit a pull request with a clear description of the changes and their purpose. Follow the existing code style and conventions, and ensure all tests pass before submitting.

## Support

For support, please open an issue in the GitHub repository with a detailed description of the problem, including steps to reproduce, expected behavior, and actual behavior. Include information about your CKAN version, extension version, and relevant configuration settings. The maintainers will respond as promptly as possible to address your concerns.

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)

This extension is licensed under the GNU Affero General Public License v3.0 or later (AGPLv3+). See the LICENSE file for more details. This license ensures that any modifications or derivative works remain open source and freely available to the community.
