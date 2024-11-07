from django.core.management import BaseCommand
import csv
from bs4 import BeautifulSoup
import requests
import urllib.request
from datetime import date
from datetime import timedelta
import time
from .modules.csv import get_header
from .modules.sensor_type import get_sensor_type
import json
from .modules.get_env_vars import get_sensor_archive_url


def register(dictionary, key, url):
    print("sensor type not in queue: register sensor type", key, end="\r")
    dictionary[key] = get_header(url)


def skip(key):
    print("sensor type", key, "already in queue: skip...", end="\r")


class Command(BaseCommand):
    help = """
    Gets header from a csv file.
    The date of the most recent csv file should be inserted as date arg to update header constantly.
    Check if the csv file of the date is already existing on archive before executing.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            type=str,
            help="Date of the most recent csv file. Format: YYYY-MM-DD",
        )

    def handle(self, *args, **kwargs):
        website = get_sensor_archive_url()
        date = kwargs["date"]

        base_url = website + "/" + date + "/"
        page = requests.get(base_url)

        print("scanning page ...", end="\r")
        print(end="\x1b[2K")
        soup = BeautifulSoup(page.content, "html.parser")
        sensor_type_queue = dict()

        for a in soup.find_all("a", href=True):
            sensor_type = get_sensor_type(a["href"], date)

            if sensor_type != None:
                url = base_url + "/" + a["href"]

                if len(sensor_type_queue) == 0:
                    register(sensor_type_queue, sensor_type, url)
                else:
                    if sensor_type not in sensor_type_queue.keys():
                        register(sensor_type_queue, sensor_type, url)
                    else:
                        skip(sensor_type)

        print(end="\x1b[2K")
        print("writing file ...")
        with open("sensor_csv_header.json", "w") as file:
            file.write(json.dumps(sensor_type_queue))
        print("see in root path: ./sensor_csv_header.json")
