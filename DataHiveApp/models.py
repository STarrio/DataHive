from django.db import models
from django.contrib.postgres.fields import ArrayField


# Create your models here.
class DataSet(models.Model):
    title = models.CharField(max_length=250)
    abstract = models.TextField(null=True, blank=True)
    link = models.URLField()
    creation_date = models.DateTimeField()
    categories = models.ManyToManyField('Category')


class Category(models.Model):
    name = models.CharField(max_length=150)


class File(models.Model):
    name = models.CharField(max_length=250)
    attributes = ArrayField(models.CharField(max_length=100), null=True, blank=True)
    dataset = models.ForeignKey('DataSet', related_name='files', on_delete=models.CASCADE)


all_models = {
    "DataSet": DataSet,
    "Category": Category,
    "File": File
}