#! /usr/bin/python3

import os
import sys
import django

SITE_ROOT = os.path.abspath(os.path.dirname(__name__))
sys.path.append(SITE_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DataHive.settings")
django.setup()

from django.db import transaction
from DataHiveApp.models import DataSet, File
import DataverseScraper


def load_datasets(datasets):
    bulk_datasets = []
    for d in datasets:
        # insert description at a Whoosh instance
        description = d['description']
        del d['description']

        bulk_datasets.append(DataSet(**d))

    return DataSet.objects.bulk_create(bulk_datasets)


def load_files(files, created_datasets):
    bulk_files = [File(**dict({'dataset': d}, **f))
                  for d, dataset_files in zip(created_datasets, files)
                  for f in dataset_files]
    File.objects.bulk_create(bulk_files)

@transaction.atomic
def load_data(datasets, files):
    created_datasets = load_datasets(datasets)
    load_files(files, created_datasets)
    return created_datasets[0]


if __name__ == '__main__':
    datasets, files = DataverseScraper.DataverseScraper().scrape_data(range(1, 2))
    load_data(datasets, files)

