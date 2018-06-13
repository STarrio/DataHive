from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone

REPOS = (
    ("DATAVERSE", "Harvard Dataverse"),
    ("KAGGLE", "Kaggle"),
    ("UCI", "UCI - Machine Learning Repository")
)


# Create your models here.
class DataSet(models.Model):

    title = models.CharField(max_length=250)
    authors = ArrayField(models.CharField(max_length=250), null=True, blank=True)
    abstract = models.TextField(null=True, blank=True)
    url = models.URLField(unique=True)
    publication_date = models.DateTimeField()
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
            "KAGGLE": (lambda x: x)
            ,
            "UCI": (lambda x: x)
        }

        return get_url[str(self.source)](self.files.all())

    def __str__(self):
        return "{0} ({1})".format(self.title, self.source)


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)


class File(models.Model):
    id_in_source = models.CharField(max_length=250)
    name = models.CharField(max_length=250)
    attributes = ArrayField(models.CharField(max_length=100), null=True, blank=True)
    size = models.CharField(max_length=20, blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    dataset = models.ForeignKey('DataSet', related_name='files', on_delete=models.CASCADE)

    def get_file_download_url(self):

        dataverse_file_download_url = "https://dataverse.harvard.edu/api/access/datafiles/{0}"
        uci_file_download_url = ""
        kaggle_file_download_url = ""

        # TODO: define kaggle/uci functions
        get_url = {
            'DATAVERSE': lambda: dataverse_file_download_url.format(self.id_in_source)
            ,
            "KAGGLE": (lambda x: x)
            ,
            "UCI": (lambda x: x)
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