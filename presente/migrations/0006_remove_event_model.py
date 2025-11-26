# Remove event field and Event model after data migration

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('presente', '0005_migrate_events_to_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activity',
            name='event',
        ),
        migrations.DeleteModel(
            name='Event',
        ),
    ]
