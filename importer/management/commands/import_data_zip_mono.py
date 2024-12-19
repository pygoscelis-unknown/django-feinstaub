"""
Imports data from a particular zip file available on:
    `http://archive.sensor.community/csv_per_month/`
Doesn't use multiprocessing.
"""

import time
import csv
import urllib.request
import zipfile
from django.core.management import BaseCommand
from .modules.create_object import create
from .modules.get_env_vars import get_sensor_archive_url
from .modules.convert_values import main as convert_values
from .modules.csv import delete_sensor_data_files
from .modules.show_progress import show_download_progress


class Command(BaseCommand):
    """
    Downloads a zip file of the specified sensor type, unzips them,
    and loads data from the extracted csv file into database.
    """

    help = """
    Loads data from a zipped csv file into database.
    """

    def add_arguments(self, parser):
        parser.add_argument("--year", type=str, help="Format: YYYY")
        parser.add_argument("--month", type=str, help="Format: MM")
        parser.add_argument(
            "--type", type=str, help="The name of the target sensor type"
        )

    def handle(self, *args, **kwargs):

        base_url = get_sensor_archive_url()
        year = kwargs["year"]
        month = kwargs["month"]
        date = year + "-" + month
        sensor_type = kwargs["type"]
        url = (
            base_url
            + "/csv_per_month/"
            + date
            + "/"
            + date
            + "_"
            + sensor_type
            + ".zip"
        )
        file_name = date + "_" + sensor_type

        start = time.time()
        object_count = 0

        print("Downloading zip ...")
        urllib.request.urlretrieve(url, file_name + ".zip", show_download_progress)
        with zipfile.ZipFile(file_name + ".zip", "r") as zip_ref:
            print("Extracting zip ...", end="\r")
            zip_ref.extractall("./")

        with open(file_name + ".csv", newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=";")

            index = 0
            header = []

            for row in reader:
                # ignore first header row
                if index == 0:
                    for i in range(len(row)):
                        header.append(row[i])
                    index += 1

                else:
                    new_row = convert_values(sensor_type, header, row)
                    create(sensor_type, new_row)

                    object_count += 1
                    print(str(object_count) + ". object created.", end="\r")

        delete_sensor_data_files(file_name)

        print("Total:", object_count, "objects")

        end = time.time()
        total_time = end - start
        print("Time:", total_time)
