from flask import Flask, render_template, request, redirect
import os
import csv
import json
import pandas as pd

from myGameLog.myGameLog import (
    create_game_folders,
    create_hardware_folders,
    create_platform_descriptions,
    create_website_structure,
    create_first_local_update_csv,
    update_local_updates_csv,
    update_platform_hardware,
    generate_qr_codes,
)

app = Flask(__name__)

website_directory = os.path.join("static", "collection")
localCSV = os.path.join("static", "local_updates_hardware.csv")
zip_file_directory = os.path.join("static", "qr_codes")
qr_codes_directory = os.path.join("static", "qr_codes")


def create_collection(xml_file_directory):
    # Create the games list
    create_game_folders(xml_file_directory, website_directory)

    # Create the hardware list
    create_hardware_folders(xml_file_directory, website_directory)

    # Create the platform description
    create_platform_descriptions(xml_file_directory, website_directory)

    # Create the website structure
    create_website_structure(website_directory)

    # # Create / update local CSV
    create_local_update_csv()


def create_local_update_csv():
    if os.path.exists(localCSV):
        update_local_updates_csv(website_directory, localCSV)
    else:
        create_first_local_update_csv(website_directory, localCSV)

    update_platform_hardware(website_directory, localCSV)


def generate_qr_code(server_url):
    server_url = server_url + "static/collection/index.html?platform="

    generate_qr_codes(
        website_directory, server_url, zip_file_directory, qr_codes_directory
    )


@app.route("/", methods=["GET", "POST"])
def index():
    message = None

    if request.method == "POST":
        if "xml_file" in request.files:
            xml_file = request.files["xml_file"]
            if xml_file:
                # Call the function to process the CSV file
                xml_file_directory = os.path.join("collection_xml", xml_file.filename)
                xml_file.save(xml_file_directory)
                try:
                    create_collection(xml_file_directory)
                    message = "Collection updated with success!"
                except:
                    message = "Error! Please check the server logs!"

        elif "edit_local_info" in request.form:
            if os.path.exists(localCSV):
                return redirect("/edit_local_csv")
            else:
                message = "Please import a collection using the XML file first!"

        elif "generate_qr_code" in request.form:
            # Call the function to generate QR code
            if os.path.exists(localCSV):
                try:
                    serverURL = request.base_url
                    generate_qr_code(serverURL)
                except:
                    message = "Error! Please check the server logs!"
                return render_template(
                    "index.html", qr_code_link=zip_file_directory + ".zip"
                )
            else:
                message = "Please import a collection using the XML file first!"

    return render_template("index.html", message=message)


# Views for the CRUD application


# create new CSV entry
@app.route("/create", methods=["GET", "POST"])
def create():
    # HTTP GET method
    if request.method == "GET":
        # get CSV fields from string query paramater
        fields = json.loads(request.args.get("fields").replace("'", '"'))

        # render HTML page dynamically
        return render_template("create_new_hardware.html", fields=fields)


@app.route("/edit_local_csv")
def edit_local_csv():
    # variable to hold CSV data
    data = []

    # read data from CSV file
    with open(localCSV, encoding="utf-8") as f:
        # create CSV dictionary reader instance
        reader = csv.DictReader(f)

        # init CSV dataset
        [data.append(dict(row)) for row in reader]

    annotated_df = pd.read_csv(localCSV, encoding="utf-8")
    unique_platforms = annotated_df["platform"].unique()
    # redirect to the proper template
    return render_template(
        "edit_local_information.html",
        data=data,
        list=list,
        len=len,
        str=str,
        unique_platforms=unique_platforms,
    )


# update existing CSV row
@app.route("/update", methods=["GET", "POST"])
def update():
    # HTTP GET method
    if request.method == "GET":
        # updated data
        data = []

        # open CSV file
        with open(localCSV, encoding="utf-8") as rf:
            # create CSV dictionary reader
            reader = csv.DictReader(rf)

            # init CSV rows
            [data.append(dict(row)) for row in reader]

            return render_template(
                "update_local_entry.html", fields=data[int(request.args.get("id"))]
            )

    # HTTP POST method
    elif request.method == "POST":
        annotated_df = pd.read_csv(localCSV, encoding="utf-8")
        hash = dict(request.form)["hash"]
        for key, val in dict(request.form).items():
            if key != "Id":
                annotated_df.loc[annotated_df["hash"] == hash, [key]] = val

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
        annotated_df.to_csv(localCSV, encoding="utf-8")
        update_platform_hardware(website_directory, localCSV)

        return redirect("/edit_local_csv")


@app.route("/delete")
def delete():
    annotated_df = pd.read_csv(localCSV, encoding="utf-8")

    row = int(request.args.get("id"))

    annotated_df.drop(annotated_df[annotated_df.index == row].index, inplace=True)

    annotated_df.index = range(len(annotated_df))

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

    annotated_df.to_csv(localCSV)
    update_platform_hardware(website_directory, localCSV)

    return redirect("/edit_local_csv")


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
