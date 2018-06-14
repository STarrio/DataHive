
from django.db import migrations
from django.db import transaction
from search_engine.whoosh_functions import create_schema


@transaction.atomic
def populate_db(apps, schema_editor):
    create_schema()


class Migration(migrations.Migration):
    dependencies = [
        ('DataHiveApp', 'initial_data'),
    ]

    operations = [
        migrations.RunPython(populate_db)
    ]
