from django.core.management import BaseCommand
import csv
import os

from bs4 import BeautifulSoup
import urllib.request
import zipfile
import datetime
import time
from .modules.sensor_type import get_sensor_type
from .modules.multiprocessing import main as create_objects

import multiprocessing

from django.apps import apps

# command example
# python manage.py import_data-all-multiprocessing --url http://archive.sensor.community --year 2024 --month 03 --app test_app

class Command(BaseCommand):
    help = 'Load data from csv file into the database'

    def add_arguments(self, parser):
        parser.add_argument('--url', type=str)
        parser.add_argument('--year', type=str)
        parser.add_argument('--month', type=str)
        parser.add_argument('--app', type=str)
        #parser.add_argument('--type', type=str)

    def handle(self, *args, **kwargs):

        base_url = kwargs['url']
        year = kwargs['year']
        month = kwargs['month']
        app = kwargs['app']
        date = year + '-' + month

        # get all sensor types
        sensor_types = []
        for m in apps.get_app_config(app).get_models():
            sensor_types.append(m.__name__)

        start = time.time()

        for t in sensor_types:
            url = base_url + "/csv_per_month/" + date + "/" + date + "_" + t + ".zip"

            try:
                file_name = date + "_" + t
                print("Downloading zip ...", end="\r")
                urllib.request.urlretrieve(url, file_name + ".zip")
                with zipfile.ZipFile(file_name + ".zip", 'r') as zip_ref:
                    print("Extracting zip ...")
                    zip_ref.extractall("./")

                with open(file_name + '.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=';')
                    rows = [x for x in reader]
                    header = rows.pop(0)

                    create_objects(t, header, rows)

                # delete csv and zip
                for f in [file_name + ".zip", file_name + ".csv"]:
                    if os.path.exists(f):
                        print("Deleting file {} ...".format(f))
                        os.remove(f)
                        print("File {} deleted.".format(f))
                    else:
                      print("Failed to delete file {}.".format(f))

            except Exception as e:
                print(f'Error: {url}: {str(e)}')

        end = time.time()
        total_time = end - start
        print("time:", total_time)
