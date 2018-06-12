
from django.db import migrations
from django.db import transaction
from DataHiveApp.models import RepoMetadata, REPOS

@transaction.atomic
def populate_db(apps, schema_editor):
    if not RepoMetadata.objects.all().exists():
        RepoMetadata.objects.bulk_create([RepoMetadata(id=i+1, name=repo[0]) for i, repo in enumerate(REPOS)])


class Migration(migrations.Migration):
    dependencies = [
        ('DataHiveApp', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_db)
    ]
