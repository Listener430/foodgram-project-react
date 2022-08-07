import csv

from django.apps import apps
from django.core.management.base import BaseCommand

"""python manage.py loadfile"""
""" --path "./static/data/genre.csv" --model_name "Genre"""
"""--app_name "foodgram"""


class Command(BaseCommand):
    help = "python manage.py loadfile --option"

    def add_arguments(self, parser):
        parser.add_argument("--path", type=str, help="file path")
        parser.add_argument("--model_name", type=str, help="model name")
        parser.add_argument("--app_name", type=str, help="app name")

    # flake8: noqa: C901
    def handle(self, *args, **options):
        file_path = options["path"]
        _model = apps.get_model(options["app_name"], options["model_name"])
        with open(file_path, "r", encoding="utf8") as csv_file:
            reader = csv.reader(csv_file, delimiter=";", quotechar="|")
            ingr_total = []
            x = 1
            for row in reader:
                ingr1 = _model(x, row[0], row[1], row[2])
                x += 1
                ingr_total.append(ingr1)
            if ingr_total:
                _model.objects.bulk_create(ingr_total)
                print("Загрузилось")
