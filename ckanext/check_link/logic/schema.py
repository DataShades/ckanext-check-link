from ckan.logic.schema import validator_args


@validator_args
def url_check(
    not_missing,
    json_list_or_string,
    default,
    convert_to_json_if_string,
    boolean_validator,
):
    return {
        "url": [not_missing, json_list_or_string],
        "patch": [default("{}"), convert_to_json_if_string],
        "save_report": [default(False), boolean_validator],
    }


@validator_args
def resource_check(not_missing, resource_id_exists, boolean_validator, default):
    return {
        "id": [not_missing, resource_id_exists],
        "save_report": [default(False), boolean_validator],
    }


@validator_args
def base_search_check(boolean_validator, default, int_validator):
    return {
        "save_report": [default(False), boolean_validator],
        "include_drafts": [default(False), boolean_validator],
        "include_deleted": [default(False), boolean_validator],
        "include_private": [default(False), boolean_validator],
        "start": [default(0), int_validator],
        "rows": [default(10), int_validator],
    }


@validator_args
def package_check(not_missing, package_id_or_name_exists):
    return dict(base_search_check(), id=[not_missing, package_id_or_name_exists])


@validator_args
def organization_check(not_missing, convert_group_name_or_id_to_id):
    return dict(base_search_check(), id=[not_missing, convert_group_name_or_id_to_id])


@validator_args
def group_check(not_missing, group_id_or_name_exists):
    return dict(base_search_check(), id=[not_missing, group_id_or_name_exists])


@validator_args
def user_check(not_missing, convert_user_name_or_id_to_id):
    return dict(base_search_check(), id=[not_missing, convert_user_name_or_id_to_id])


@validator_args
def search_check(unicode_safe, default):
    return dict(base_search_check(), fq=[default("*:*"), unicode_safe])


@validator_args
def report_save(unicode_safe, resource_id_exists, ignore_missing, not_missing, default, convert_to_json_if_string):
    return {
        "id": [ignore_missing, unicode_safe],
        "url": [not_missing, unicode_safe],
        "resource_id": [ignore_missing, resource_id_exists],
        "details": [default("{}"), convert_to_json_if_string],
    }


@validator_args
def report_show(unicode_safe, ignore_missing, resource_id_exists):
    return {
        "id": [ignore_missing, unicode_safe],
        "url": [ignore_missing, unicode_safe],
        "resource_id": [ignore_missing, resource_id_exists],
    }


@validator_args
def report_search(unicode_safe, default):
    return {}


@validator_args
def report_delete(unicode_safe, not_missing):
    return {
        "id": [not_missing, unicode_safe]
    }