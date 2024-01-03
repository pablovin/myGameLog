from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import os
import segno
from glob import glob

import shutil

from myGameLog.utils import remove_last_empty_row


def update_platform_hardware(website_directory, local_csv):
    local_df = pd.read_csv(local_csv, encoding="utf-8")

    for platform, platform_df in local_df.groupby("platform"):
        platform_directory = os.path.join(website_directory, "platforms", platform)
        platform_df.to_csv(
            os.path.join(platform_directory, "hardware_list.csv"),
            lineterminator="\n",
        )

        remove_last_empty_row(os.path.join(platform_directory, "hardware_list.csv"))

        print(f"Updated platform: {platform}")


def update_local_updates_csv(website_directory, local_csv):
    readFrom = glob(os.path.join(website_directory, "platforms/*"))

    allCSV = []

    for platform in readFrom:
        hard_list = os.path.join(platform, "hardware_list.csv")
        if os.path.exists(hard_list):
            allCSV.append(pd.read_csv(hard_list))

    new_df = pd.concat(allCSV)

    new_df = new_df[
        [
            "name",
            "hash",
            "platform",
            "releaseDate",
            "buyingDate",
            "cib",
            "region",
            "edition",
            "imageUrl",
            "power",
            "video",
            "mods",
            "location",
        ]
    ]

    annotated_df = pd.read_csv(local_csv, encoding="utf-8")

    annotated_df = annotated_df[
        [
            "name",
            "hash",
            "platform",
            "releaseDate",
            "buyingDate",
            "cib",
            "region",
            "edition",
            "imageUrl",
            "power",
            "video",
            "mods",
            "location",
        ]
    ]

    new_df.index = range(len(new_df))
    annotated_df.index = range(len(new_df))

    merged_df = new_df.merge(
        annotated_df[
            ["name", "hash", "buyingDate", "power", "video", "mods", "location"]
        ],
        on=["hash"],
        how="left",
        suffixes=("", "_annotated"),
    )

    new_df["power"] = merged_df["power_annotated"].combine_first(new_df["power"])
    new_df["video"] = merged_df["video_annotated"].combine_first(new_df["video"])
    new_df["mods"] = merged_df["mods_annotated"].combine_first(new_df["mods"])
    new_df["location"] = merged_df["location_annotated"].combine_first(
        new_df["location"]
    )

    new_df.to_csv(local_csv)
    print(f"Local update list updated at: {local_csv}")


def create_first_local_update_csv(website_directory, localCSV):
    readFrom = glob(os.path.join(website_directory, "platforms/*"))

    allCSV = []

    for platform in readFrom:
        hard_list = os.path.join(platform, "hardware_list.csv")
        if os.path.exists(hard_list):
            allCSV.append(pd.read_csv(hard_list))

    allCSV = pd.concat(allCSV)

    allCSV = allCSV[
        [
            "name",
            "platform",
            "hash",
            "releaseDate",
            "buyingDate",
            "cib",
            "region",
            "edition",
            "imageUrl",
            "power",
            "video",
            "mods",
            "location",
        ]
    ]

    allCSV.to_csv(localCSV)

    print(f"Local update list created at: {localCSV}")


def create_website_structure(website_directory):
    shutil.copy(os.path.join("myGameLog", "webpages", "index.html"), website_directory)
    shutil.copy(os.path.join("myGameLog", "images", "notFound.jpeg"), website_directory)

    print(f"Website created!")


def generate_qr_codes(
    website_directory, server_url, zip_file_directory, save_qr_codes_directory
):
    for platform in os.listdir(os.path.join(website_directory, "platforms")):
        if not os.path.exists(save_qr_codes_directory):
            os.makedirs(save_qr_codes_directory)

        qrcode = segno.make_qr(os.path.join(server_url, platform))
        qrcode.save(os.path.join(save_qr_codes_directory, f"{platform}.png"), scale=5)

        print(f"Saved QR Code for: {platform}.")

    archived = shutil.make_archive(zip_file_directory, "zip", save_qr_codes_directory)

    print(f"QRCode zip available at: {archived}.")


def create_platform_descriptions(xml_directory, website_directory):
    with open(xml_directory, "r", encoding="utf8") as f:
        data = f.read()

        bs_data = BeautifulSoup(data, "xml")

        entries = bs_data.find_all("game")

        platforms = {}

        # Looking for hardware info
        for b in entries:
            is_hardware = int(b.hardware.text)

            try:
                console = b.hardwarecategory.displayname.text
            except:
                console = "-"

            collection = b.collection.displayname.text

            if (
                is_hardware
                and collection == "My game collection"
                and console == "Console"
            ):
                thisDF = {}

                platform = b.platform.text
                platform = (
                    platform.replace("/", "").replace("  ", " ").replace(" ", "_")
                )

                thisDF["name"] = b.platform.text
                thisDF["summary"] = b.description

                try:
                    thisDF["logo"] = b.coverfrontdefault.text
                except:
                    thisDF["logo"] = "notFound.jpeg"

                thisDF = pd.DataFrame(thisDF, index=[platform])

                if not platform in platforms.keys():
                    platforms[platform] = thisDF

    saveIn = os.path.join(website_directory, "platforms/")

    for platform in platforms.keys():
        thisPlatformFolder = os.path.join(saveIn, platform)

        if not os.path.exists(thisPlatformFolder):
            os.makedirs(thisPlatformFolder)

        plat_df = platforms[platform]

        plat_df.to_csv(
            os.path.join(thisPlatformFolder, "platform_description.csv"),
            lineterminator="\n",
        )

        remove_last_empty_row(
            os.path.join(thisPlatformFolder, f"platform_description.csv")
        )

        print(f"Saved description for: {platform}.")


def create_hardware_folders(xml_directory, website_directory):
    with open(xml_directory, "r", encoding="utf8") as f:
        data = f.read()

        bs_data = BeautifulSoup(data, "xml")

        # print(bs_data)

        entries = bs_data.find_all("game")

        platforms = {}

        # Looking for hardware info
        for b in entries:
            is_hardware = int(b.hardware.text)
            collection = b.collection.displayname.text
            if is_hardware and collection == "My game collection":
                # if "3DO" in b.platform.text:
                #     print(b)
                #     break
                thisDF = {}

                platform = b.platform.text
                platform = (
                    platform.replace("/", "").replace("  ", " ").replace(" ", "_")
                )

                hard_cat = b.hardwarecategory.displayname.text

                thisDF["name"] = b.title.text

                thisDF["hash"] = b.hash.text

                thisDF["platform"] = platform
                try:
                    thisDF["releaseDate"] = b.releasedate.displaydate.text
                except:
                    thisDF["releaseDate"] = "-"

                try:
                    thisDF["buyingDate"] = b.purchasedate.displaydate.text
                except:
                    thisDF["buyingDate"] = "-"

                thisDF["cib"] = b.completeness.text
                thisDF["region"] = b.location.displayname.text

                thisDF["edition"] = "-"

                try:
                    thisDF["imageUrl"] = b.coverfrontdefault.text
                except:
                    try:
                        thisDF["imageUrl"] = b.coverfront.text
                    except:
                        thisDF["imageUrl"] = "notFound.jpeg"

                if hard_cat == "Console":
                    thisDF["power"] = (
                        "230V (eu)"
                        if b.location.displayname.text == "Pal"
                        else f"110V ({b.location.displayname.text})"
                    )
                    thisDF["video"] = "Composite"
                    thisDF["mods"] = "[None]"
                    thisDF["location"] = "Box 1"
                else:
                    thisDF["power"] = "-"
                    thisDF["video"] = "-"
                    thisDF["mods"] = "[None]"
                    thisDF["location"] = "Box 1"

                thisDF = pd.DataFrame(thisDF, index=[b.title.text])

                if platform in platforms.keys():
                    platforms[platform].append(thisDF)
                else:
                    platforms[platform] = []
                    platforms[platform].append(thisDF)

    saveIn = os.path.join(website_directory, "platforms/")

    for platform in platforms.keys():
        thisPlatformFolder = os.path.join(saveIn, platform)

        if not os.path.exists(thisPlatformFolder):
            os.makedirs(thisPlatformFolder)

        plat_df = pd.concat(platforms[platform])

        plat_df.to_csv(
            os.path.join(thisPlatformFolder, "hardware_list.csv"), lineterminator="\n"
        )

        remove_last_empty_row(os.path.join(thisPlatformFolder, f"hardware_list.csv"))

        print(f"Saved Hardware for: {platform}. Total hardware items: {len(plat_df)}")


def create_game_folders(xml_directory, website_directory):
    with open(xml_directory, "r", encoding="utf8") as f:
        data = f.read()
        bs_data = BeautifulSoup(data, "xml")
        entries = bs_data.find_all("game")

        platforms = {}

        for b in entries:
            is_hardware = int(b.hardware.text)
            collection = b.collection.displayname.text

            if not is_hardware and collection == "My game collection":
                platform = b.platform.text
                platform = (
                    platform.replace("/", "").replace("  ", " ").replace(" ", "_")
                )

                thisDF = {}
                thisDF["name"] = b.title.text
                try:
                    thisDF["releaseDate"] = b.releasedate.displaydate.text
                except:
                    thisDF["releaseDate"] = "-"

                try:
                    thisDF["buyingDate"] = b.purchasedate.displaydate.text
                except:
                    thisDF["buyingDate"] = "-"

                try:
                    thisDF["genre"] = b.genre.displayname.text
                except:
                    thisDF["genre"] = "-"

                try:
                    thisDF["completed"] = b.completiondate.text
                except:
                    thisDF["completed"] = "No"

                thisDF["cib"] = b.completeness.text

                try:
                    thisDF["region"] = b.region.displayname.text
                except:
                    thisDF["region"] = "No"

                thisDF["edition"] = "-"

                try:
                    thisDF["imageUrl"] = b.coverfrontdefault.text
                except:
                    thisDF["imageUrl"] = "notFound.jpeg"

                thisDF = pd.DataFrame(thisDF, index=[b.title.text])

                if platform in platforms.keys():
                    platforms[platform].append(thisDF)
                else:
                    platforms[platform] = []
                    platforms[platform].append(thisDF)

    saveIn = os.path.join(website_directory, "platforms/")

    for platform in platforms.keys():
        thisPlatformFolder = os.path.join(saveIn, platform)

        if not os.path.exists(thisPlatformFolder):
            os.makedirs(thisPlatformFolder)

        plat_df = pd.concat(platforms[platform])

        plat_df.to_csv(
            os.path.join(thisPlatformFolder, "games_list.csv"), lineterminator="\n"
        )

        remove_last_empty_row(os.path.join(thisPlatformFolder, f"games_list.csv"))

        print(f"Saved Games for: {platform}. Total games: {len(plat_df)}")
