# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import base64
import fnmatch
import hashlib
import json
import logging
import os
import shutil
from typing import Any
from urllib import request

import boto3
from botocore.exceptions import ClientError

# Boto lex client
lex_client = boto3.client("lexv2-models", region_name="us-east-1")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def bot_start_export(bot_id: str, bot_version: str):
    try:
        response = lex_client.create_export(
            resourceSpecification={"botExportSpecification": {"botId": bot_id, "botVersion": bot_version}},
            fileFormat="LexJson",
        )
        return response

    except Exception as e:
        logger.error("Lex describe bot call failed")
        logger.error(e)


def wait_on_export(export_id, delay, max_attempts):
    waiter = lex_client.get_waiter("bot_export_completed")
    waiter.wait(exportId=export_id, WaiterConfig={"Delay": delay, "MaxAttempts": max_attempts})


def get_export_url(export_id: str):
    try:
        response = lex_client.describe_export(exportId=export_id)
        return response["downloadUrl"]

    except Exception as e:
        logger.error("Lex describe export call failed")
        logger.error(e)
        return None


def create_upload_url():
    try:
        response = lex_client.create_upload_url()
        return response

    except Exception as e:
        logger.error("Lex create upload url call failed")
        logger.error(e)
        return None


def bot_start_import(import_id: str, bot_name: str, role_arn: str, strategy: str):
    try:
        response = lex_client.start_import(
            importId=import_id,
            resourceSpecification={
                "botImportSpecification": {
                    "botName": bot_name,
                    "roleArn": role_arn,
                    "dataPrivacy": {"childDirected": False},
                }
            },
            mergeStrategy=strategy,
        )
        return response

    except Exception as e:
        logger.error("Lex bot start import call failed")
        logger.error(e)


def wait_on_import(import_id: str, delay: int, max_attempts: int):
    waiter = lex_client.get_waiter("bot_import_completed")
    waiter.wait(importId=import_id, WaiterConfig={"Delay": delay, "MaxAttempts": max_attempts})


def delete_bot_export(export_id: str):
    try:
        lex_client.delete_export(exportId=export_id)
    except Exception as e:
        logger.error("Lex delete bot export call failed")
        logger.error(e)


def delete_bot_import(import_id: str):
    try:
        lex_client.delete_import(importId=import_id)

    except Exception as e:
        logger.error("Lex delete bot import call failed")
        logger.error(e)


def list_bots(name: str, value: str, operator: str):
    try:
        resp = lex_client.list_bots(
            filters=[
                {
                    "name": name,
                    "values": [
                        value,
                    ],
                    "operator": operator,
                },
            ]
        )
        bots = resp["botSummaries"]

        while "nextToken" in resp:
            resp = lex_client.list_bots(
                filters=[
                    {
                        "name": name,
                        "values": [
                            value,
                        ],
                        "operator": operator,
                    },
                ],
                nextToken=resp["nextToken"],
            )
            bots = bots + (resp["botSummaries"])

        return bots

    except Exception as e:
        logger.error("Lex list bots call failed")
        logger.error(e)


def describe_bot(bot_id):
    try:
        resp = lex_client.describe_bot(botId=bot_id)
        return resp

    except Exception as e:
        logger.error("Lex describe bot call failed")
        logger.error(e)


def list_bot_locales(bot_id, bot_version):
    try:
        resp = lex_client.list_bot_locales(botId=bot_id, botVersion=bot_version)
        locales_summaries = resp["botLocaleSummaries"]

        while "nextToken" in resp:
            resp = lex_client.list_bot_locales(botId=bot_id, botVersion=bot_version, nextToken=resp["nextToken"])
            locales_summaries = locales_summaries + resp["botLocaleSummaries"]

        return locales_summaries

    except Exception as e:
        logger.error("Lex list bot locales call failed")
        logger.error(e)


def describe_bot_locale(bot_id, bot_version, locale):
    try:
        resp = lex_client.describe_bot_locale(botId=bot_id, botVersion=bot_version, localeId=locale)
        return resp

    except Exception as e:
        logger.error("Lex describe bot locale failed")
        logger.error(e)


def list_bot_versions(bot_id):
    try:
        resp = lex_client.list_bot_versions(botId=bot_id)
        bot_versions = resp["botVersionSummaries"]

        while "nextToken" in resp:
            resp = lex_client.list_bot_versions(botId=bot_id, nextToken=resp["nextToken"])
            bot_versions = bot_versions + resp["botVersionSummaries"]

        return bot_versions

    except Exception as e:
        logger.error("Lex list bot versions call failed")
        logger.error(e)


def describe_bot_version(bot_id, bot_version):
    try:
        resp = lex_client.describe_bot_version(botId=bot_id, botVersion=bot_version)
        return resp

    except Exception as e:
        logger.error("Lex describe bot version call failed")
        logger.error(e)


def list_bot_aliases(bot_id):
    try:
        resp = lex_client.list_bot_aliases(botId=bot_id)
        bot_aliases = resp["botAliasSummaries"]

        while "nextToken" in resp:
            resp = lex_client.list_bot_aliases(botId=bot_id, nextToken=resp["nextToken"])
            bot_aliases = bot_aliases + resp["botAliasSummaries"]

        return bot_aliases

    except Exception as e:
        logger.error("Lex list bot aliases call failed")
        logger.error(e)


def describe_bot_alias(bot_id, bot_alias_id):
    try:
        resp = lex_client.describe_bot_alias(botAliasId=bot_alias_id, botId=bot_id)
        return resp

    except Exception as e:
        logger.error("Lex describe bot alias call failed")
        logger.error(e)


def list_intents(bot_id, bot_version, locale):
    try:
        resp = lex_client.list_intents(botId=bot_id, botVersion=bot_version, localeId=locale)
        intents = resp["intentSummaries"]

        while "nextToken" in resp:
            resp = lex_client.list_intents(
                botId=bot_id,
                botVersion=bot_version,
                localeId=locale,
                nextToken=resp["nextToken"],
            )
            intents = intents + resp["intentSummaries"]

        return intents

    except Exception as e:
        logger.error("Lex list bot intents call failed")
        logger.error(e)


def describe_intent(bot_id, intent_id, bot_version, locale):
    try:
        resp = lex_client.describe_intent(intentId=intent_id, botId=bot_id, botVersion=bot_version, localeId=locale)
        return resp

    except Exception as e:
        logger.error("Lex describe intents call failed")
        logger.error(e)


def describe_slot_type(bot_id, bot_version, slot_type_id, locale):
    try:
        resp = lex_client.describe_slot_type(
            slotTypeId=slot_type_id,
            botId=bot_id,
            botVersion=bot_version,
            localeId=locale,
        )
        return resp

    except Exception as e:
        logger.error("Lex describe slot type call failed")
        logger.error(e)


def list_slots(bot_id, bot_version, locale, intent_id):
    try:
        resp = lex_client.list_slots(botId=bot_id, botVersion=bot_version, localeId=locale, intentId=intent_id)
        slots = resp["slotSummaries"]

        while "nextToken" in resp:
            resp = lex_client.list_slots(
                botId=bot_id,
                botVersion=bot_version,
                localeId=locale,
                intentId=intent_id,
                nextToken=resp["nextToken"],
            )
            slots = slots + (resp["slotSummaries"])

        return slots

    except Exception as e:
        logger.error("Lex list slots call failed")
        logger.error(e)


def get_zip_bytes(zip_file):
    with open(zip_file, "rb") as zip_data:
        bot_bytes = zip_data.read()

    return bot_bytes


def get_url_bytes(url: str):
    with request.urlopen(url) as bot_zip:
        bot_bytes = bot_zip.read()

    return bot_bytes


def clear_directory(target_dir: str):
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
        os.makedirs(target_dir)
    return


def get_secret(secret_name):
    logger.debug("In get secret")
    # Create a Secrets Manager client
    client = boto3.client("secretsmanager")

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        logger.debug("Client Error: %s", e.response)
        if e.response["Error"]["Code"] == "DecryptionFailureException":
            logger.error("Secrets Manager can't decrypt the protected secret text using the provided KMS key.")
            raise e
        elif e.response["Error"]["Code"] == "InternalServiceErrorException":
            logger.error("An error occurred on the server side.")
            raise e
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            logger.error("You provided an invalid value for a parameter.")
            raise e
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            logger.error("You provided a parameter value that is not valid for the current state of the resource.")
            raise e
        elif e.response["Error"]["Code"] == "ResourceNotFoundException":
            logger.error("We can't find the resource that you asked for.")
            raise e
        return None
    else:
        # logger.debug("Secret Response: %s", get_secret_value_response) # DSR Fix
        # Decrypts secret using the associated KMS key.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if "SecretString" in get_secret_value_response:
            return get_secret_value_response["SecretString"]
        else:
            return base64.b64decode(get_secret_value_response["SecretBinary"])


def replace_slot_type_id_recursively(obj, id_map):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "slotTypeId" and value in id_map:
                obj[key] = id_map[value]
            else:
                replace_slot_type_id_recursively(value, id_map)
    elif isinstance(obj, list):
        for _index, item in enumerate(obj):
            replace_slot_type_id_recursively(item, id_map)


def reformat_json_file(file_path, id_map, update_slot_type_id=False):
    with open(file_path, encoding="utf8") as f:
        data = json.load(f)

    original_identifier = data.get("identifier", "")
    if len(original_identifier) == 10:
        if not update_slot_type_id:
            if original_identifier not in id_map:
                identifier_path = file_path.split("LexBot/", 1)[1]
                # identifier_path = os.path.split(file_path)[-1]
                new_identifier = generate_unique_identifier(identifier_path)
                id_map[original_identifier] = new_identifier
            else:
                new_identifier = id_map[original_identifier]

            data["identifier"] = new_identifier
        else:
            replace_slot_type_id_recursively(data, id_map)

    with open(file_path, "w") as f:
        sorted_obj = sort_keys_recursively(data)
        json.dump(sorted_obj, f, indent=4)
        f.write("\n")


def reformat_json_files(root_dir):
    id_map: dict[str, Any] = {}
    # First pass to update the identifiers and populate the id_map
    for dirpath, _dirnames, filenames in os.walk(root_dir):
        for filename in fnmatch.filter(filenames, "*.json"):
            file_path = os.path.join(dirpath, filename)
            reformat_json_file(file_path, id_map)

    # Second pass to update the slotTypeId values
    for dirpath, _dirnames, filenames in os.walk(root_dir):
        for filename in fnmatch.filter(filenames, "*.json"):
            file_path = os.path.join(dirpath, filename)
            reformat_json_file(file_path, id_map, update_slot_type_id=True)


def sort_keys_recursively(obj):
    """
    Recursively sorts the keys of a JSON object and sorts lists of dictionaries by the "priority" key if present.
    """
    if isinstance(obj, dict):
        return {k: sort_keys_recursively(v) for k, v in sorted(obj.items())}
    elif isinstance(obj, list):
        # Check if the list contains dictionaries with the "priority" key
        if all(isinstance(elem, dict) and "priority" in elem for elem in obj):
            # Sort the list by the "priority" key
            obj = sorted(obj, key=lambda x: x["priority"])
        return [sort_keys_recursively(elem) for elem in obj]
    else:
        return obj


def generate_unique_identifier(s: str, length: int = 10) -> str:
    # Create an MD5 hash object
    hash_object = hashlib.md5()

    # Update the hash object with the input string
    hash_object.update(s.encode("utf-8"))

    # Get the hexadecimal digest of the hash
    hex_digest = hash_object.hexdigest()

    # Return the first 'length' characters of the hash
    return hex_digest[:length]
