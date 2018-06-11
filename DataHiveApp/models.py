from django.db import models
from django.contrib.postgres.fields import ArrayField


# Create your models here.
class DataSet(models.Model):

    REPOS = (
        ("DATAVERSE", "Harvard Dataverse"),
        ("KAGGLE", "Kaggle"),
        ("UCI", "UCI - Machine Learning Repository")
    )

    title = models.CharField(max_length=250)
    authors = ArrayField(models.CharField(max_length=100), null=True, blank=True)
    abstract = models.TextField(null=True, blank=True)
    url = models.URLField(unique=True)
    publication_date = models.DateTimeField()
    keywords = ArrayField(models.CharField(max_length=150), null=True, blank=True)
    source = models.CharField(max_length=20, choices=REPOS, default="DATAVERSE")
    categories = models.ManyToManyField('Category', blank=True)

    def get_files_download_url(self):

        dataverse_file_download_url = "https://dataverse.harvard.edu/api/access/datafiles/{0}"
        uci_file_download_url = ""
        kaggle_file_download_url = ""

        # TODO: define kaggle/uci functions
        switch = {
            'DATAVERSE': lambda files: dataverse_file_download_url.format(",".join([f.id_in_source for f in files]))
            ,
            "KAGGLE": (lambda x: x)
            ,
            "UCI": (lambda x: x)

        }

        return switch[str(self.source)](self.files.all())

    def __str__(self):
        return "{0} ({1})".format(self.title, self.source)


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)


class File(models.Model):
    id_in_source = models.CharField(max_length=100)
    name = models.CharField(max_length=250)
    attributes = ArrayField(models.CharField(max_length=100), null=True, blank=True)
    dataset = models.ForeignKey('DataSet', related_name='files', on_delete=models.CASCADE)

    def __str__(self):
        return "{0} -- {1}".format(self.name, self.dataset)


all_models = {
    "DataSet": DataSet,
    "Category": Category,
    "File": File
}