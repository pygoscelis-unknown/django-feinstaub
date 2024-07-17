from django.core.management import BaseCommand
import os
import csv
from bs4 import BeautifulSoup
import requests
import urllib.request
from datetime import date
from datetime import timedelta
import time
from .modules.csv import get_header
from .modules.sensor_type_queue import register, skip
import json
import textwrap

class Command(BaseCommand):
    help = "generate base files from json"

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)
        parser.add_argument('--app', type=str)

    def handle(self, *args, **kwargs):
        path = kwargs['path']
        apps_name = kwargs['app']


        # --- GET HEADER DATA --- #
        with open(path) as f:
            data = json.load(f)

        # --- INIT FILES --- #
        app_basefiles = [
            "models.py",
            "admin.py",
            "serializers.py",
            "views.py",
            "urls.py"
        ]

        app_commandfiles = [
            "create_object.py"
        ]

        project_filenames = [
            "p_urls.py"
        ]

        with open(app_basefiles[0], "w") as pyf:
            pyf.write(textwrap.dedent("""\
                from django.db import models
            """))

        with open(app_basefiles[1], "w") as pyf:
            pyf.write(textwrap.dedent("""\
                from django.contrib import admin
            """))

        with open(app_basefiles[2], "w") as pyf:
            pyf.write(textwrap.dedent("""\
                from rest_framework import serializers
            """))

        with open(app_basefiles[3], "w") as pyf:
            pyf.write(textwrap.dedent("""\
                from rest_framework import viewsets
            """))

        with open(app_basefiles[4], "w") as pyf:
            pyf.write(textwrap.dedent("""\
                from django.urls import path, include
                from rest_framework import routers
            """))

        with open(project_filenames[0], "w") as pyf:
            pyf.write(textwrap.dedent("""\
                from django.contrib import admin
                from django.urls import path, include
                from django.contrib.auth.models import User
                from rest_framework import routers, serializers, viewsets
            """))

        with open(app_commandfiles[0], "w") as pyf:
            pyf.write("")


        # --- ITERATE OVER OBJECTS --- #
        index = 0
        for key, values in data.items():
            key = key.replace("-", "")


            with open(app_basefiles[0], "a") as pyf:
                pyf.write(textwrap.dedent("""\
                    class {}(models.Model):
                """.format(key)))

                for value in values:
                    if value == "sensor_id"\
                            or value == "location":
                        pyf.write(textwrap.dedent("""\
                        #
                            {} = models.IntegerField(null=True, blank=True)
                        """).format(value))
                    elif value == "sensor_type":
                        pyf.write(textwrap.dedent("""\
                        #
                            {} = models.CharField(max_length=255, blank=True)
                        """).format(value))
                    elif value == "timestamp":
                        pyf.write(textwrap.dedent("""\
                        #
                            {} = models.DateTimeField(null=True, blank=True)
                        """).format(value))
                    else:
                        pyf.write(textwrap.dedent("""\
                        #
                            {} = models.FloatField(null=True, blank=True)
                        """).format(value))


            # --- IMPORT MODELS --- #
            with open(app_basefiles[1], "a") as pyf:
                if index == 0:
                    pyf.write("from .models import {}".format(key))
                else:
                    if index == len(data) - 1:
                        pyf.write(", {}\n".format(key))
                    else:
                        pyf.write(", {}".format(key))

            with open(app_basefiles[2], "a") as pyf:
                if index == 0:
                    pyf.write("from .models import {}".format(key))
                else:
                    if index == len(data) - 1:
                        pyf.write(", {}\n".format(key))
                    else:
                        pyf.write(", {}".format(key))

            with open(app_basefiles[3], "a") as pyf:
                if index == 0:
                    pyf.write("from .models import {}".format(key))
                else:
                    if index == len(data) - 1:
                        pyf.write(", {}\n".format(key))
                    else:
                        pyf.write(", {}".format(key))

            with open(app_commandfiles[0], "a") as pyf:
                if index == 0:
                    pyf.write("from {}.models import {}".format(apps_name, key))
                else:
                    if index == len(data) - 1:
                        pyf.write(", {}\n".format(key))
                    else:
                        pyf.write(", {}".format(key))

            index += 1



        # --- APP_MODELS.PY --- #
        with open(app_basefiles[0], "r") as pyf:
            lines = pyf.readlines()

        with open(app_basefiles[0], "w") as pyf:
            for line in lines:
                if line.strip("\n") != "#":
                    pyf.write(line)


        # --- CREATE_OBJECT.PY --- #
        with open(app_commandfiles[0], "a") as pyf:
            pyf.write("def create(sensor_type, row):\n")


        # --- ITERATE OVER OBJECTS --- #
        index = 0
        for key, values in data.items():
            key = key.replace("-", "")

            # --- APP_ADMIN.PY --- #
            with open(app_basefiles[1], "a") as pyf:
                pyf.write("admin.site.register({})\n".format(key))

            # --- APP_VIEWS.PY --- #
            with open(app_basefiles[3], "a") as pyf:
                if index == 0:
                    pyf.write("from .serializers import {}Serializer".format(key.capitalize()))
                else:
                    if index == len(data) - 1:
                        pyf.write(", {}Serializer\n".format(key.capitalize()))
                    else:
                        pyf.write(", {}Serializer".format(key.capitalize()))

            # --- APP_SERIALIZERS.PY --- #
            with open(app_basefiles[2], "a") as pyf:
                pyf.write(textwrap.dedent("""\
                    class {}Serializer(serializers.HyperlinkedModelSerializer):
                        class Meta:
                            model = {}
                            fields = "__all__"
                """.format(key.capitalize(), key)))

            # --- APP_URLS.PY --- #
            with open(app_basefiles[4], "a") as pyf:
                if index == 0:
                    pyf.write("from .views import {}ViewSet".format(key.capitalize()))
                else:
                    if index == len(data) - 1:
                        pyf.write(", {}ViewSet\n".format(key.capitalize()))
                    else:
                        pyf.write(", {}ViewSet".format(key.capitalize()))

            # --- CREATE_OBJECT.PY --- #
            with open(app_commandfiles[0], "a") as pyf:
                pyf.write(textwrap.dedent("""\
                #
                    if sensor_type == "{}":
                        command = {}.objects.create(
                """.format(key, key)))

                subindex = 0
                for value in values:
                    pyf.write(textwrap.dedent("""\
                    #
                            {}=row[{}],
                    """).format(value, subindex))
                    subindex += 1

                pyf.write(textwrap.dedent("""\
                #
                        )
                """))


            index += 1

        # --- APP_URLS.PY --- 
        with open(app_basefiles[4], "a") as pyf:
            pyf.write("router = routers.DefaultRouter()\n")


        # --- ITERATE OVER OBJECTS --- #
        index = 0
        for key, values in data.items():
            key = key.replace("-", "")

            # --- APP_VIEWS.PY --- #
            with open(app_basefiles[3], "a") as pyf:
                pyf.write(textwrap.dedent("""\
                    class {}ViewSet(viewsets.ModelViewSet):
                        queryset = {}.objects.all()
                        serializer_class = {}Serializer
                """.format(key.capitalize(), key, key.capitalize())))


            # --- APP_URLS.PY --- 
            with open(app_basefiles[4], "a") as pyf:
                pyf.write("router.register(r'{}', {}ViewSet)\n".format(key, key.capitalize()))


        # --- CREATE_OBJECT.PY --- #
        with open(app_commandfiles[0], "a") as pyf:
            pyf.write(textwrap.dedent("""\
                #
                    return command
            """))

        with open(app_commandfiles[0], "r") as pyf:
            lines = pyf.readlines()

        with open(app_commandfiles[0], "w") as pyf:
            for line in lines:
                if line.strip("\n") != "#":
                    pyf.write(line)


        # --- APP_URLS.PY --- #
        with open(app_basefiles[4], "a") as pyf:
            pyf.write(textwrap.dedent("""\
                urlpatterns = [
                    path('', include(router.urls)),
                ]
            """))


        # --- PROJECT_URLS.PY --- #
        with open(project_filenames[0], "a") as pyf:
            pyf.write(textwrap.dedent("""\
                class UserSerializer(serializers.HyperlinkedModelSerializer):
                    class Meta:
                        model = User
                        fields = ['url', 'username', 'email', 'is_staff']
                class UserViewSet(viewsets.ModelViewSet):
                    queryset = User.objects.all()
                    serializer_class = UserSerializer
                router = routers.DefaultRouter()
                router.register(r'users', UserViewSet)
                urlpatterns = [
                    path('admin/', admin.site.urls),
                    path('', include(router.urls)),
                    path('{}/', include('{}.urls')),
                    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
                ]
            """.format(apps_name, apps_name)))

        if os.path.exists("{}".format(apps_name)):
            for filename in app_basefiles:
                os.replace(filename, "{}/{}".format(apps_name, filename))
        else:
            print("Target app folder is missing! Aborting ...")
            for d in [app_basefiles, app_commandfiles, project_filenames]:
                for filename in d:
                    os.remove(filename)

        if os.path.exists("{}/management/commands".format(apps_name)):
            for filename in app_commandfiles:
                os.replace(filename, "{}/management/commands/{}".format(apps_name, filename))
        else:
            print("Target app command folder is missing! Aborting ...")
            for d in [app_basefiles, app_commandfiles, project_filenames]:
                for filename in d:
                    os.remove(filename)
