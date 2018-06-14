#! /usr/bin/python3

import os
import sys
import django

SITE_ROOT = os.path.abspath(os.path.dirname(__name__))
sys.path.append(SITE_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DataHive.settings")
django.setup()

from django.db import transaction
from DataHiveApp.models import DataSet, File, RepoMetadata, Category
import DataverseScraper
import UCIScraper
from search_engine import whoosh_functions


def load_datasets(datasets, categories):
    bulk_datasets = []
    whoosh_data = []
    for d in datasets:
        # insert description at a Whoosh instance
        description = d['description'].replace("\"", " ") if d['description'] is not None else None
        abstract = d['abstract'].replace("\"", " ") if d['abstract'] is not None else None

        whoosh_data.append({'abstract': abstract, 'description': description})

        del d['description']
        del d['abstract']

        bulk_datasets.append(DataSet(**d))

    created_datasets = DataSet.objects.bulk_create(bulk_datasets)

    whoosh_functions.insert_docs([dict({'dataset_id': str(d.id)}, **wh) for wh, d in zip(whoosh_data, created_datasets)])

    for c, d in zip(categories, created_datasets):
        d.categories.set([cat[0].id for cat in c])
    return created_datasets


def load_files(files, created_datasets):
    bulk_files = [File(**dict({'dataset': d}, **f))
                  for d, dataset_files in zip(created_datasets, files)
                  for f in dataset_files]
    File.objects.bulk_create(bulk_files)


def load_categories(categories):
    created_categories = []
    for c in categories:
        if type(c) == 'list':
            created_categories.append([Category.objects.get_or_create(name=cat) for cat in c])
        else:
            created_categories.append([Category.objects.get_or_create(name=c)])
    return created_categories


@transaction.atomic
def load_data_verse(repo, num_pages):
    """ Execute scraping, insert datasets/files into db and update repository metadata """
    page_range = range(repo.last_fetch_page + 1, repo.last_fetch_page + 1 + num_pages)

    datasets, files = DataverseScraper.DataverseScraper().scrape_data(page_range)
    created_categories = []
    created_datasets = load_datasets(datasets, created_categories)
    load_files(files, created_datasets)

    last_created_dataset = created_datasets[-1]
    repo.last_fetch_page = repo.last_fetch_page + 1 + num_pages
    repo.last_fetch_dataset = last_created_dataset
    repo.save()


@transaction.atomic
def load_data_uci():
    """ Execute scraping from UCI Dataset Repository """
    datasets, files, categories = UCIScraper.UCIScraper().scrape_data()
    created_categories = load_categories(categories)
    created_datasets = load_datasets(datasets, created_categories)

    load_files(files,created_datasets)


if __name__ == '__main__':
    repo_name_dv = 'DATAVERSE'
    repo_dv = RepoMetadata.objects.get(name=repo_name_dv)

    #load_data_uci()
    for _ in range(1):
        load_data_verse(repo_dv, 1)


