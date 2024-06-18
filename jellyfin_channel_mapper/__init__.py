import os
import csv
import argparse
import time

from jellyfin.api import JellyfinAPI
from dotenv import load_dotenv
from prompt_toolkit.shortcuts import (
    radiolist_dialog,
    message_dialog,
    input_dialog,
    ProgressBar,
)

from thefuzz import fuzz
from thefuzz import process

load_dotenv()

JELLYFIN_API_TOKEN = os.getenv("JELLYFIN_API_TOKEN")
JELLYFIN_SERVER_ENDPOINT = os.getenv("JELLYFIN_SERVER_ENDPOINT")


def main():
    parser = argparse.ArgumentParser(description="Process import or export commands.")
    parser.add_argument("command", choices=["import", "export"], help="command to run")

    args = parser.parse_args()

    api = JellyfinAPI(endpoint=JELLYFIN_SERVER_ENDPOINT, api_token=JELLYFIN_API_TOKEN)
    if args.command == "import":
        import_mappings(api)
    elif args.command == "export":
        export_mappings(api)


def import_mappings(api: JellyfinAPI):

    listing_providers = api.get_livetv_listing_providers()

    # ask user to select provider
    provider_id = radiolist_dialog(
        title="EPG Guide",
        text="Which EPG Guide do you want to fuzz?",
        values=[(provider.id, provider.path) for provider in listing_providers],
    ).run()

    # Print the selected option
    print(f"You selected: {provider_id}")

    mapping_options = api.get_channel_mapping_options(provider_id=provider_id)

    # show stats

    message_dialog(
        title="EPG Guide",
        text=f"We pulled {len(mapping_options.mappings)} current mappings. {len(mapping_options.tuner_channels)} available tuner channels and {len(mapping_options.provider_channels)} EPG provider channels",
    ).run()

    # as Id, Name, ProviderChannelId, ProviderChannelName
    generated_mappings = []

    provider_names = [m.name for m in mapping_options.provider_channels]
    for tuner_channel in mapping_options.tuner_channels:
        if "ES" in tuner_channel.name:
            selected_provider, score = process.extractOne(
                tuner_channel.name, provider_names, scorer=fuzz.partial_ratio
            )
            if score > 85:
                print(
                    f"Tuner Channel: {tuner_channel.name} -> {selected_provider} with score {score}"
                )
                generated_mappings.append(
                    [
                        tuner_channel.id,
                        tuner_channel.name,
                        selected_provider,
                        selected_provider,
                    ]
                )

    message_dialog(
        title="Matching result",
        text=f"We matched {len(generated_mappings)}",
    ).run()

    csv_file = input_dialog(
        title="Create matches CSV", text="Save to CSV file name:"
    ).run()

    # write provider channel list
    with open("provider_channel_list.csv", "w", newline="") as csvfile:
        writer = csv.writer(
            csvfile, delimiter=";", quotechar="\\", quoting=csv.QUOTE_MINIMAL
        )
        writer.writerow(["ProviderChannelId", "ProviderChannelName"])
        for pc in mapping_options.provider_channels:
            writer.writerow([pc.id, pc.name])

    # write fuzzed mappings
    with open(csv_file, "w", newline="") as csvfile:
        writer = csv.writer(
            csvfile, delimiter=";", quotechar="\\", quoting=csv.QUOTE_MINIMAL
        )
        writer.writerow(["Id", "Name", "ProviderChannelId", "ProviderChannelName"])
        for m in generated_mappings:
            writer.writerow(m)


def export_mappings(api: JellyfinAPI):
    listing_providers = api.get_livetv_listing_providers()

    # ask user to select provider
    provider_id = radiolist_dialog(
        title="EPG Guide",
        text="Which EPG Guide do you want to fuzz?",
        values=[(provider.id, provider.path) for provider in listing_providers],
    ).run()

    csv_file = input_dialog(
        title="Open CSV", text="Type filename of CSV file to export:"
    ).run()

    with open(csv_file, newline="") as csvfile:
        reader = csv.reader(csvfile)
        with ProgressBar() as progress:
            for row in progress(reader):
                api.set_channel_mapping(
                    tuner_channel_id=row[0],
                    provider_id=provider_id,
                    provider_channel_id=row[2],
                )
                time.sleep(0.1)


if __name__ == "__main__":
    main()
