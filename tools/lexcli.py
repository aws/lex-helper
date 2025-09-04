import concurrent.futures
import datetime
import filecmp
import io
import json
import os
import shutil
import sys
import time
import zipfile
from uuid import uuid4

import bot_export_helpers as helpers
import boto3
import click
import colorlog
import pandas as pd
from botocore.config import Config

# Optional import for export functionality
try:
    import regenerate_enums
except ImportError:
    regenerate_enums = None

# Get the path to the current directory
base_path = os.path.dirname(os.path.abspath(__file__))

color_log = colorlog.getLogger()

# Add the module root to sys.path
module_path = os.path.join(base_path, "lambdas/fulfillment_function")
sys.path.append(module_path)


@click.group()
def main():
    """
    lexcli is a command-line tool for managing Lex, here are some of the features:
    """
    pass


@main.command()
@click.argument("environment_name")
@click.option("--project-root", "-p", default="../examples/sample_airline_bot", help="Path to project root directory")
def export(environment_name: str, project_root: str):
    """
    Export a Lex bot
    """
    bot_name = f"{environment_name}LexBot"
    original_bot_name = "LexBot"
    bot_list = helpers.list_bots("BotName", bot_name, "EQ")
    bot_version = "DRAFT"
    target_dir = "temp"
    bot_id = None
    # looking for just one
    if len(bot_list) == 1:
        bot_id = bot_list[0]["botId"]

    if not bot_id:
        print(f"No ID for bot name {bot_name}", flush=True)
        exit(3)

    # create directory if it does not exist, and make sure it's empty
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    helpers.clear_directory("temp")

    # source bot ID
    print(f"BOT EXPORT ID: {bot_id}", flush=True)

    print("Starting bot export...", flush=True)
    # TODO - integrate SecretsManager to secure zip file
    export_resp = helpers.bot_start_export(bot_id, bot_version)

    print("Waiting on export...", flush=True)
    helpers.wait_on_export(export_resp["exportId"], 10, 30)
    print("Export Complete.", flush=True)

    print("Retrieving export...", flush=True)
    url = helpers.get_export_url(export_resp["exportId"])
    bot_zip_bytes = helpers.get_url_bytes(url)

    # write zip as is
    zip_name = target_dir + "/" + bot_name + ".zip"
    with open(zip_name, "wb") as bot_zip_file:
        bot_zip_file.write(bot_zip_bytes)

    print("Saving bot export to files.", flush=True)
    with zipfile.ZipFile(io.BytesIO(bot_zip_bytes)) as zip_data:
        zip_data.extractall(target_dir)

    print("Deleting bot export job.", flush=True)
    helpers.delete_bot_export(export_resp["exportId"])

    # rewrite original botName in file
    with open(target_dir + "/" + bot_name + "/Bot.json") as bot_json:
        bot_data = json.load(bot_json)
        bot_data["name"] = original_bot_name

    with open(target_dir + "/" + bot_name + "/Bot.json", "w") as bot_json:
        bot_json.write(json.dumps(bot_data))

    # rename bot
    os.rename(target_dir + "/" + bot_name, target_dir + "/" + original_bot_name)

    # Reformat all JSON
    helpers.reformat_json_files("temp")

    # Update Intents
    update_directories(
        os.path.join(project_root, "lex-export/LexBot/BotLocales/en_US/Intents"),
        "temp/LexBot/BotLocales/en_US/Intents",
        "intent",
    )

    # Update Slots
    update_directories(
        os.path.join(project_root, "lex-export/LexBot/BotLocales/en_US/SlotTypes"),
        "temp/LexBot/BotLocales/en_US/SlotTypes",
        "slotType",
    )

    # Regenerate slots enum (if available)
    if regenerate_enums:
        print("Regenerating slot enums...")
        regenerate_enums.regenerate_slot_enums(project_root)

        # Regenerate intents enum
        print("Regenerating intents enum...")
        regenerate_enums.regenerate_intent_enum(project_root)
    else:
        print("Skipping enum regeneration (regenerate_enums module not found)")


def are_dir_trees_equal(dir1: str, dir2: str):
    """
    Compare two directories recursively. Files in each directory are
    assumed to be equal if their names and contents are equal.

    @param dir1: First directory path
    @param dir2: Second directory path

    @return: True if the directory trees are the same and
        there were no errors while accessing the directories or files,
        False otherwise.
    """

    dirs_cmp = filecmp.dircmp(dir1, dir2)
    if len(dirs_cmp.left_only) > 0 or len(dirs_cmp.right_only) > 0 or len(dirs_cmp.funny_files) > 0:
        return False
    (_, mismatch, errors) = filecmp.cmpfiles(dir1, dir2, dirs_cmp.common_files, shallow=False)
    if len(mismatch) > 0 or len(errors) > 0:
        return False
    for common_dir in dirs_cmp.common_dirs:
        new_dir1 = os.path.join(dir1, common_dir)
        new_dir2 = os.path.join(dir2, common_dir)
        if not are_dir_trees_equal(new_dir1, new_dir2):
            return False
    return True


def update_directories(existing_dir: str, updated_dir: str, directory_type: str):
    # List the directories in each path
    existing_dirs = {name for name in os.listdir(existing_dir) if os.path.isdir(os.path.join(existing_dir, name))}
    updated_dirs = {name for name in os.listdir(updated_dir) if os.path.isdir(os.path.join(updated_dir, name))}

    # Find directories that exist in both places, or only in one place
    common_dirs = existing_dirs & updated_dirs
    existing_only_dirs = existing_dirs - updated_dirs
    updated_only_dirs = updated_dirs - existing_dirs

    # For directories that exist in both places, check if they are different
    for directory in common_dirs:
        if not are_dir_trees_equal(os.path.join(existing_dir, directory), os.path.join(updated_dir, directory)):
            # If directories are different, ask the user which one to keep
            user_input = input(
                f"Found a conflict for {directory_type} '{directory}', would you like to replace what's in the repository with the one that you exported? (If you didn't mean to change it, say n) (y/n): "
            )
            if user_input.lower() == "y":
                shutil.rmtree(os.path.join(existing_dir, directory))  # remove existing directory
                shutil.copytree(
                    os.path.join(updated_dir, directory),
                    os.path.join(existing_dir, directory),
                )  # copy updated directory

    # For directories that exist only in the existing directory, ask the user what to do
    for directory in existing_only_dirs:
        user_input = input(
            f"The repository contains {directory_type} '{directory}', but your bot export doesn't have it, Do you want to keep it? (If you're not sure, say y) (y/n): "
        )
        if user_input.lower() == "n":
            shutil.rmtree(os.path.join(existing_dir, directory))  # remove the existing directory

    # For directories that exist only in the updated directory, copy them to the existing directory
    for directory in updated_only_dirs:
        shutil.copytree(os.path.join(updated_dir, directory), os.path.join(existing_dir, directory))  # copy new directory


# Continuously query Lex for testing if it's up or down.  Good for seeing how long Lex is down during a deployment, etc.
@main.command()
@click.argument("bot_id")
@click.argument("alias_id")
def ping(bot_id: str, alias_id: str):
    """
    This function pings the bot over and over.  Please provide the bot_id and alias_id, should look something like PDAVUMACRC and YPLG2LUS9V.
    This will call the bot every second, print the status of the bot, and write the status with a timestamp to a file called
    status-of-bot.txt
    """
    my_config = Config(
        region_name="us-east-1",
        signature_version="v4",
        retries={"max_attempts": 10, "mode": "standard"},
    )
    client = boto3.client("lexv2-runtime", config=my_config)
    # Create and open file called status-of-bot.txt, if it exists, replace it
    file_output = open("status-of-bot.txt", "w")
    print("Pinging bot every second, press Ctrl+C to stop")
    while True:
        try:
            # Generate random session Id
            session_id = str(uuid4())
            # Get bot status
            response = client.recognize_text(
                botId=bot_id,
                botAliasId=alias_id,
                localeId="en_US",
                text="I have a peanut allergy",
                sessionId=session_id,
            )
            bot_status = response["messages"][0]["content"]

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if bot_status == "I can assist you with your question":
                color_log.info("Bot is up")
                # Write timestamp on newline in file with status of UP, with the timestamp formatted human readable

                file_output.write(f"{timestamp}: Bot is UP\n")

            else:
                color_log.error("Bot is down")
                file_output.write(f"{timestamp}: Bot is DOWN\n")
            time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopped by user")
            break


@main.command()
@click.argument("test_set")
@click.argument("environment_name")
@click.argument("bot_version")
@click.option("--update_baseline", is_flag=True, help="Update the baseline golden test set")
def analytics_test(
    test_set: str,
    environment_name: str,
    bot_version: str = "DRAFT",
    update_baseline: bool = False,
):
    """
    Loads a test set of utterances from a CSV under golden_test_sets/test_set.csv, then queries Lex for each utterance.
    """

    bot_name = f"{environment_name}LexBot"

    bot_list = helpers.list_bots("BotName", bot_name, "EQ")
    bot_id = None
    # looking for just one
    if bot_list and len(bot_list) == 1:
        bot_id = bot_list[0].get("botId")

    if not bot_id:
        print(f"No ID for bot name {bot_name}", flush=True)
        exit(3)

    # Get the botAliasId for the bot version
    bot_alias_list = helpers.list_bot_aliases(bot_id)
    bot_alias_id = None
    if not bot_alias_list:
        print("No bot aliases found")
        exit(3)

    for bot_alias in bot_alias_list:
        if bot_alias.get("botVersion") == bot_version:
            bot_alias_id = bot_alias.get("botAliasId")
            print("Found bot alias ID: " + str(bot_alias_id))

    if not bot_alias_id:
        print("No bot alias ID found")
        exit(3)

    # Load CSV
    test_set_path = f"golden_test_sets/data/{test_set}.csv"
    test_set_df = pd.read_csv(test_set_path)

    # Query lex for each utterance using a fresh session ID each time
    my_config = Config(
        region_name="us-east-1",
        signature_version="v4",
        retries={"max_attempts": 10, "mode": "standard"},
    )
    client = boto3.client("lexv2-runtime", config=my_config)

    success_counter = 0
    failure_counter = 0

    def query_lex(row):
        row = row[1]

        session_id = str(uuid4())
        response = client.recognize_text(
            botId=bot_id,
            botAliasId=bot_alias_id,
            localeId="en_US",
            text=row["Input"],
            sessionId=session_id,
        )
        interpretations = response["interpretations"]
        top_interpretation = interpretations[0]
        detected_intent_name = top_interpretation.get("intent", {}).get("name")
        detected_intent_score = top_interpretation.get("nluConfidence", {}).get("score")
        expected_intent_name = row["Expected Output Intent"]

        # Update dataframe
        test_set_df.loc[row.name, "Detected Intent"] = detected_intent_name
        test_set_df.loc[row.name, "Detected Intent Score"] = detected_intent_score

        if detected_intent_name == expected_intent_name:
            # Update dataframe
            test_set_df.loc[row.name, "Result"] = "Pass"

            color_log.info(f"✅ {row['Input']} ({expected_intent_name}, {detected_intent_score})")

            return 1
        else:
            # Update dataframe
            test_set_df.loc[row.name, "Result"] = "Fail"

            color_log.error(f"❌ {row['Input']}")
            color_log.error(f"    - Expected: {expected_intent_name}")
            color_log.error(f"    - Received: {detected_intent_name, detected_intent_score}")
            return 0

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(query_lex, test_set_df.iterrows())

    for result in results:
        success_counter += result
        failure_counter += 1 - result

    # Group passes and fails by intent
    test_set_df["Result"] = test_set_df["Result"].astype("category")
    test_set_df["Result"].cat.set_categories(["Pass", "Fail"])
    test_set_df["Expected Output Intent"] = test_set_df["Expected Output Intent"].astype("category")
    test_set_df["Expected Output Intent"].cat.set_categories(test_set_df["Expected Output Intent"].unique())

    # Calculate percentage of tests passed
    test_set_df["Percent"] = test_set_df["Result"].apply(lambda x: 1 if x == "Pass" else 0).astype(int)
    total_tests = len(test_set_df)
    pass_count = test_set_df["Percent"].sum()
    percentage = round((pass_count / total_tests) * 100, 2)

    # Print a table with percentage
    print("\n--- 🎬 Updated Summary for " + test_set + " Golden Test Set 🎬 ---")
    summary_table = test_set_df.groupby(["Expected Output Intent", "Result"], observed=True).size().unstack(fill_value=0)
    # If Pass or Fail is not set, add them to the table
    if "Pass" not in summary_table.columns:
        summary_table["Pass"] = 0
    if "Fail" not in summary_table.columns:
        summary_table["Fail"] = 0
    summary_table["Percentage"] = round(summary_table["Pass"] / (summary_table["Pass"] + summary_table["Fail"]) * 100, 2)
    print(summary_table)

    # Print Summary
    print("\nOverall:")
    print(f"✅ {success_counter} tests passed")
    print(f"❌ {failure_counter} tests failed")
    print(f"📊 {percentage}% accuracy")

    print("--------------------------------------------------------------")

    # Load golden_test_set_baseline.csv to compare results
    baseline_path = f"golden_test_sets/baselines/{test_set}_Baseline.csv"
    if not os.path.exists(baseline_path):
        print("No baseline found, creating one")
        test_set_df.to_csv(baseline_path, index=False)
        baseline_df = test_set_df
    baseline_df = pd.read_csv(baseline_path)
    test_set_df["Detected Intent"] = test_set_df["Detected Intent"].astype("category")
    test_set_df["Detected Intent"].cat.set_categories(test_set_df["Detected Intent"].unique())
    # Add percent column
    test_set_df["Percent"] = test_set_df["Result"].apply(lambda x: 1 if x == "Pass" else 0)

    # Compare results, print differences, and overall result
    # For each row that is different, print the row number, input, and show the baseline vs. updated results

    print("\n--- 🏆 Comparison to Baseline 🏆 ---")
    print("Baseline Score: " + baseline_df["Result"].value_counts().to_string())
    print("\nUpdated Score: " + test_set_df["Result"].value_counts().to_string() + "\n")

    # Without modifying the baseline or test_set dataframes, create a new dataframe with only the rows that are different
    # This will be used to print the differences
    differences_df = pd.concat([baseline_df, test_set_df]).drop_duplicates(keep=False)
    differences_df = differences_df.sort_values(by=["Input"])

    # Show the overall percentage improvement or decline (in green or red)
    baseline_success_counter = baseline_df["Result"].value_counts().get("Pass")
    baseline_failure_counter = baseline_df["Result"].value_counts().get("Fail")

    # Show the overall percentage improvement or decline (in green or red)
    baseline_success_counter = baseline_df["Result"].value_counts().get("Pass")
    baseline_failure_counter = baseline_df["Result"].value_counts().get("Fail")
    if baseline_success_counter is None:
        baseline_success_counter = 0
    if baseline_failure_counter is None:
        baseline_failure_counter = 0
    baseline_total_tests = baseline_success_counter + baseline_failure_counter
    baseline_percentage = baseline_success_counter / baseline_total_tests * 100
    # Round percentage to 2 decimal places
    baseline_percentage = round(baseline_percentage, 2)

    # Calculate percentage difference
    percentage_difference = percentage - baseline_percentage
    # Round percentage difference to 2 decimal places
    percentage_difference = round(percentage_difference, 2)

    # Print percentage difference
    if percentage_difference > 0:
        color_log.info(f"📈 {percentage_difference}% improvement")
    elif percentage_difference < 0:
        color_log.error(f"📉 {percentage_difference}% decline")
    else:
        print("📊 No change")

    # Save dataframe with results to CSV
    print("\n")
    if update_baseline:
        color_log.info("Note", "Updated baseline golden test set scores")
        test_set_df.to_csv(baseline_path, index=False)
    else:
        print("Not updating baseline golden test set scores, pass --update_baseline to update")


if __name__ == "__main__":
    main()
