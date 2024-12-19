import datetime
from bs4 import BeautifulSoup
from django.core.management import BaseCommand
from .modules.sensor_type import get_sensor_type
from .modules.get_env_vars import get_sensor_archive_url
from .modules import requests


class Command(BaseCommand):
    """
    Prints out all sensor types whose monthly data have been saved in zip format in following json files:
    * PROJECT_ROOT/zip_filenames.json
    * PROJECT_ROOT/sensor_types-zip.json
    for more detail, visit http://archive.sensor.community/csv_per_month/
    """

    help = """
    Prints out all sensor types with monthly data in following json files:
    * PROJECT_ROOT/zip_filenames.json
    * PROJECT_ROOT/sensor_types-zip.json
    """

    def handle(self, *args, **kwargs):
        url = get_sensor_archive_url() + "/csv_per_month/"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        sensor_type_queue = {}

        filenames = [
            "zip_filenames.json",
            "sensor_types-zip.json",
        ]
        with open(filenames[0], "w", encoding="utf-8") as pyf:
            pyf.write("[\n")
        with open(filenames[1], "w", encoding="utf-8") as pyf:
            pyf.write("[\n")

        sensor_type_queue = []
        index = 0

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href[-1] == "/":
                href = href[:-1]

            try:
                datetime.datetime.strptime(href, "%Y-%m")
            except ValueError:
                continue

            page = requests.get(url + href + "/")
            soup = BeautifulSoup(page.content, "html.parser")
            date = href

            for a in soup.find_all("a", href=True):
                if href in a["href"]:
                    try:
                        sensor_type = get_sensor_type(a["href"], date, True)
                    except ValueError:
                        continue

                    with open(filenames[0], "a", encoding="utf-8") as pyf:
                        if index == 0:
                            pyf.write('"' + a["href"] + '"')
                        else:
                            pyf.write(',\n"' + a["href"] + '"')

                    if sensor_type not in sensor_type_queue:
                        sensor_type_queue.append(sensor_type)

                        with open(filenames[1], "a", encoding="utf-8") as pyf:
                            if index == 0:
                                pyf.write('"' + sensor_type + '"')
                                index += 1
                            else:
                                pyf.write(',\n"' + sensor_type + '"')
                        print("register sensor type", sensor_type, end="\r")
                    else:
                        print("sensor type already in queue, skip ...", end="\r")

        with open(filenames[0], "a", encoding="utf-8") as pyf:
            pyf.write("\n]")
        with open(filenames[1], "a", encoding="utf-8") as pyf:
            pyf.write("\n]")
