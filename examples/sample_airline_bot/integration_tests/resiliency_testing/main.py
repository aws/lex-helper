# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import json

import boto3

# Initialize boto3 Lex V2 client
lex_client = boto3.client("lexv2-models", region_name="us-east-1")

# Retrieve bot id and bot alias id from CDK outputs
with open("cdk-outputs.json") as json_file:
    va_bot = next(iter(json.load(json_file).values()))
    bot_id = va_bot.get("LexBotId")
    bot_alias_id = va_bot.get("LexBotAliasId")
    bot_name = va_bot.get("LexBotName")
    bot_alias_name = va_bot.get("LexBotAliasName")
response = lex_client.describe_bot(botId=bot_id)
idle_session_ttl_in_seconds = response["idleSessionTTLInSeconds"]
role_arn = response["roleArn"]


def main():
    # Break lex bot
    new_name = bot_name + "_SIMULATED_FAILURE"
    rename_lex_bot(bot_id, new_name)

    # Do testing
    print("Testing...")
    input("Wait for input: ")

    # Restore lex bot
    rename_lex_bot(bot_id, bot_name)
    print(f"Bot restored to its original name {bot_name}.")


def rename_lex_bot(bot_id, new_name):
    """
    Rename a given Lex v2 bot to a new name.
    """
    print(f"Bot {bot_id} being renamed to {new_name}...")
    response = lex_client.update_bot(
        botId=bot_id,
        botName=new_name,
        dataPrivacy={"childDirected": False},
        idleSessionTTLInSeconds=idle_session_ttl_in_seconds,
        roleArn=role_arn,
    )
    print(response)
    print(f"Bot {bot_id} successfully renamed to {new_name}.")
    return response


if __name__ == "__main__":
    main()
