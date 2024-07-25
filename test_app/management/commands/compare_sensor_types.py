from django.core.management import BaseCommand
import csv
import os

from bs4 import BeautifulSoup
import requests
import urllib.request
import zipfile
import datetime
from .modules.sensor_type import get_sensor_type
from .modules.create_object import create

# command example
# python manage.py compare_sensor_types --url http://archive.sensor.community 


class Command(BaseCommand):
    help = """
    Save sensor data of all monthly csv files: see http://archive.sensor.community/csv_per_month/
    """

    def add_arguments(self, parser):
        parser.add_argument("--url", type=str)

    def handle(self, *args, **kwargs):

        url = kwargs["url"] + "/csv_per_month/"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        sensor_type_queue = dict()

        filenames = [
            "list-zip_files.txt",
            "list-sensor_types.txt",
        ]
        with open(filenames[0], "w") as pyf:
            pyf.write("")
        with open(filenames[1], "w") as pyf:
            pyf.write("")

        sensor_type_queue = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href[-1] == "/":
                href = href[:-1]

            try:
                datetime.datetime.strptime(href, "%Y-%m")
                page = requests.get(url + href + "/")
                soup = BeautifulSoup(page.content, "html.parser")
                date = href

                for a in soup.find_all("a", href=True):
                    if href in a["href"]:
                        sensor_type = get_sensor_type(a["href"], date, True)
                        with open(filenames[0], "a") as pyf:
                            pyf.write(a["href"] + "\n")

                        if sensor_type not in sensor_type_queue:
                            sensor_type_queue.append(sensor_type)

                            with open(filenames[1], "a") as pyf:
                                pyf.write(sensor_type + "\n")
                                print("register sensor type", sensor_type)
                        else:
                            print("sensor type already in queue, skip ...")

            except ValueError:
                continue