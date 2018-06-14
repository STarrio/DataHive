from django.db import models
from django.contrib.postgres.fields import ArrayField
from search_engine.whoosh_functions import search_doc_by_id

REPOS = (
    ("DATAVERSE", "Harvard Dataverse"),
    ("UCI", "UCI - Machine Learning Repository")
)


# Create your models here.
class DataSet(models.Model):

    title = models.CharField(max_length=250)
    authors = ArrayField(models.CharField(max_length=250), null=True, blank=True)
    abstract = models.TextField(null=True, blank=True)
    no_instances = models.IntegerField(null=True, default=None)
    no_attr = models.IntegerField(null=True, default=None)
    url = models.URLField(unique=True)
    download_url = models.URLField(null=True)
    publication_date = models.DateTimeField(null=True)
    keywords = ArrayField(models.CharField(max_length=150), null=True, blank=True)
    source = models.ForeignKey('RepoMetadata', related_name='datasets', on_delete=models.DO_NOTHING)
    categories = models.ManyToManyField('Category', blank=True)

    def get_files_download_url(self):

        dataverse_file_download_url = "https://dataverse.harvard.edu/api/access/datafiles/{0}"
        uci_file_download_url = ""
        kaggle_file_download_url = ""

        # TODO: define kaggle/uci functions
        get_url = {
            'DATAVERSE': lambda files: dataverse_file_download_url.format(",".join([f.id_in_source for f in files]))
            ,
            "UCI": (lambda  x: None)
        }

        return get_url[str(self.source)](self.files.all())

    def get_abstract(self):
        whoosh_data = search_doc_by_id(self.id)
        return whoosh_data['abstract'] if 'abstract' in whoosh_data else None

    def get_description(self):
        whoosh_data = search_doc_by_id(self.id)
        return whoosh_data['description'] if 'description' in whoosh_data else None

    def __str__(self):
        return "{0} ({1})".format(self.title, self.source)


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class File(models.Model):
    id_in_source = models.CharField(max_length=250)
    name = models.CharField(max_length=250)
    attributes = ArrayField(models.CharField(max_length=100), null=True, blank=True)
    size = models.CharField(max_length=20, blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    dataset = models.ForeignKey('DataSet', related_name='files', on_delete=models.CASCADE)

    def get_file_download_url(self):

        dataverse_file_download_url = "https://dataverse.harvard.edu/api/access/datafiles/{0}"
        uci_file_download_url = "http://archive.ics.uci.edu/ml/"
        kaggle_file_download_url = ""

        # TODO: define kaggle/uci functions
        get_url = {
            'DATAVERSE': lambda: dataverse_file_download_url.format(self.id_in_source)
            ,
            "UCI": (lambda: self.dataset.download_url+self.id_in_source)
        }

        return get_url[str(self.dataset.source)]()

    def __str__(self):
        return "{0} -- {1}".format(self.name, self.dataset)


class RepoMetadata(models.Model):
    name = models.CharField(max_length=10, choices=REPOS, default='DATAVERSE', unique=True)
    last_fetch_page = models.IntegerField(null=True, blank=True, default=0)
    last_fetch_dataset = models.ForeignKey('DataSet', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

all_models = {
    "DataSet": DataSet,
    "Category": Category,
    "File": File,
    "RepoMetadata": RepoMetadata
}
