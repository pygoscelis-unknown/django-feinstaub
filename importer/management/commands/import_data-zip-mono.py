from django.core.management import BaseCommand
import csv
import os

from bs4 import BeautifulSoup
import urllib.request
import zipfile
import datetime
import time
import math
from .modules.sensor_type import get_sensor_type
from .modules.create_object import create
from .modules.get_env_vars import get_sensor_archive_url
from .modules.convert_values import main as convert_values
from .modules.csv import delete_sensor_data_files


class Command(BaseCommand):
    help = """
    Loads data from csv files into the database.
    This command downloads zip files of a specific sensor type available in zip format, unzip them and load data from the extracted csv files into the database.
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

        print("Downloading zip ...", end="\r")
        urllib.request.urlretrieve(url, file_name + ".zip")
        with zipfile.ZipFile(file_name + ".zip", "r") as zip_ref:
            print("Extracting zip ...", end="\r")
            zip_ref.extractall("./")

        with open(file_name + ".csv", newline="") as csvfile:
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

        print("total:", object_count, "objects", end="\r")

        end = time.time()
        total_time = end - start
        print("time:", total_time)
