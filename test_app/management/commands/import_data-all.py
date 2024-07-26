from django.core.management import BaseCommand
import csv

from bs4 import BeautifulSoup
import requests
import urllib.request
import datetime
import time
from .modules.sensor_type import get_sensor_type
from .modules.create_object import create
from .modules.get_env_vars import get_sensor_archive_url


class Command(BaseCommand):
    help = """
    Loads data from csv files into the database.
    This command loads directly data of all sensor types available in csv format into the database.
    The date must be set in the following format: YYYY-MM-DD
    """

    def add_arguments(self, parser):
        parser.add_argument("--date", type=str, help="Format: YYYY-MM-DD")

    def handle(self, *args, **kwargs):

        website = get_sensor_archive_url()
        date = kwargs["date"]
        base_url = website + "/" + date
        page = requests.get(base_url)
        soup = BeautifulSoup(page.content, "html.parser")

        start = time.time()
        object_count = 0
        for i in soup.find_all("a", href=True):
            if date in i["href"]:
                sensor_type = get_sensor_type(i["href"], date)
                sensor_type = sensor_type.replace("-", "")

                if sensor_type != None:
                    url = base_url + "/" + i["href"]

                    response = urllib.request.urlopen(url)
                    lines = [line.decode("utf-8") for line in response.readlines()]
                    reader = csv.reader(lines, delimiter=";")

                    index = 0
                    header = []

                    for row in reader:
                        # ignore first header row
                        if index == 0:
                            for i in range(len(row)):
                                header.append(row[i])
                            index += 1

                        else:
                            # ignore/convert illigal values
                            for i in range(len(row)):
                                if header[i] != "sensor_type":
                                    if (
                                        header[i] == "sensor_id"
                                        or header[i] == "location"
                                    ):
                                        # int
                                        try:
                                            row[i] = int(row[i])
                                        except ValueError:
                                            row[i] = None

                                    elif header[i] == "timestamp":
                                        # timestamp
                                        try:
                                            row[i] = datetime.datetime.fromisoformat(
                                                row[i]
                                            )
                                        except ValueError:
                                            row[i] = None

                                    else:
                                        # float
                                        try:
                                            row[i] = float(row[i])
                                        except ValueError:
                                            row[i] = None

                            create(sensor_type, row)

                            object_count += 1
                            print(str(object_count) + ". object created.")
        print("total:", object_count, "objects")

        end = time.time()
        total_time = end - start
        print("time:", total_time)
