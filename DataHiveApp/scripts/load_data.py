#! /usr/bin/python3

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DataHive.settings")

from DataHiveApp.models import DataSet


def load_datasets(datasets):
    datasets = [DataSet(d) for d in datasets]
    DataSet.objects.builk_create(datasets)


if __name__ == '__main__':
    pass