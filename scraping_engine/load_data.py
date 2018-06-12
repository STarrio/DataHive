#! /usr/bin/python3

import os
import sys
import django

SITE_ROOT = os.path.abspath(os.path.dirname(__name__))
sys.path.append(SITE_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DataHive.settings")
django.setup()

from django.db import transaction
from DataHiveApp.models import DataSet, File, RepoMetadata
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
def load_data(repo_name, num_pages):
    """ Execute scraping, insert datasets/files into db and update repository metadata """
    repo = RepoMetadata.objects.get(name=repo_name)
    page_range = range(repo.last_fetch_page + 1, repo.last_fetch_page + 1 + num_pages)

    datasets, files = DataverseScraper.DataverseScraper().scrape_data(page_range)
    created_datasets = load_datasets(datasets)
    load_files(files, created_datasets)

    last_created_dataset = created_datasets[-1]
    repo.last_fetch_page = repo.last_fetch_page + 1 + num_pages
    repo.last_fetch_dataset = last_created_dataset
    repo.save()


if __name__ == '__main__':
    load_data('DATAVERSE', 1)


