from __future__ import annotations

from ckan import types
from ckan.logic.schema import validator_args


@validator_args
def url_check(
    not_missing: types.Validator,
    json_list_or_string: types.Validator,
    default: types.ValidatorFactory,
    convert_to_json_if_string: types.Validator,
    boolean_validator: types.Validator,
) -> types.Schema:
    return {
        "url": [not_missing, json_list_or_string],
        "save": [default(False), boolean_validator],
        "clear_available": [default(False), boolean_validator],
        "skip_invalid": [default(False), boolean_validator],
        "link_patch": [default("{}"), convert_to_json_if_string],
    }


@validator_args
def resource_check(
    not_missing: types.Validator,
    resource_id_exists: types.Validator,
    boolean_validator: types.Validator,
    default: types.ValidatorFactory,
    convert_to_json_if_string: types.Validator,
) -> types.Schema:
    return {
        "id": [not_missing, resource_id_exists],
        "save": [default(False), boolean_validator],
        "clear_available": [default(False), boolean_validator],
        "link_patch": [default("{}"), convert_to_json_if_string],
    }


@validator_args
def base_search_check(
    boolean_validator: types.Validator,
    default: types.ValidatorFactory,
    int_validator: types.Validator,
    convert_to_json_if_string: types.Validator,
) -> types.Schema:
    return {
        "save": [default(False), boolean_validator],
        "clear_available": [default(False), boolean_validator],
        "skip_invalid": [default(False), boolean_validator],
        "include_drafts": [default(False), boolean_validator],
        # "include_deleted": [default(False), boolean_validator],
        "include_private": [default(False), boolean_validator],
        "start": [default(0), int_validator],
        "rows": [default(10), int_validator],
        "link_patch": [default("{}"), convert_to_json_if_string],
    }


@validator_args
def package_check(
    not_missing: types.Validator, package_id_or_name_exists: types.Validator
) -> types.Schema:
    return dict(base_search_check(), id=[not_missing, package_id_or_name_exists])


@validator_args
def organization_check(
    not_missing: types.Validator, convert_group_name_or_id_to_id: types.Validator
) -> types.Schema:
    return dict(base_search_check(), id=[not_missing, convert_group_name_or_id_to_id])


@validator_args
def group_check(
    not_missing: types.Validator, group_id_or_name_exists: types.Validator
) -> types.Schema:
    return dict(base_search_check(), id=[not_missing, group_id_or_name_exists])


@validator_args
def user_check(
    not_missing: types.Validator, convert_user_name_or_id_to_id: types.Validator
) -> types.Schema:
    return dict(base_search_check(), id=[not_missing, convert_user_name_or_id_to_id])


@validator_args
def search_check(
    unicode_safe: types.Validator, default: types.ValidatorFactory
) -> types.Schema:
    return dict(base_search_check(), fq=[default("*:*"), unicode_safe])


@validator_args
def report_save(
    unicode_safe: types.Validator,
    resource_id_exists: types.Validator,
    ignore_missing: types.Validator,
    not_missing: types.Validator,
    default: types.ValidatorFactory,
    convert_to_json_if_string: types.Validator,
) -> types.Schema:
    return {
        "id": [ignore_missing, unicode_safe],
        "url": [not_missing, unicode_safe],
        "state": [not_missing, unicode_safe],
        "resource_id": [ignore_missing, resource_id_exists],
        "details": [default("{}"), convert_to_json_if_string],
    }


@validator_args
def report_show(
    unicode_safe: types.Validator,
    ignore_missing: types.Validator,
    resource_id_exists: types.Validator,
) -> types.Schema:
    return {
        "id": [ignore_missing, unicode_safe],
        "url": [ignore_missing, unicode_safe],
        "resource_id": [ignore_missing, resource_id_exists],
    }


@validator_args
def report_search(
    ignore_empty: types.Validator,
    default: types.ValidatorFactory,
    int_validator: types.Validator,
    boolean_validator: types.Validator,
    json_list_or_string: types.Validator,
) -> types.Schema:
    return {
        "limit": [default(10), int_validator],
        "offset": [default(0), int_validator],
        "exclude_state": [ignore_empty, json_list_or_string],
        "include_state": [ignore_empty, json_list_or_string],
        "attached_only": [default(False), boolean_validator],
        "free_only": [default(False), boolean_validator],
    }


@validator_args
def report_delete():
    return report_show()
