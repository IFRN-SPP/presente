# Data migration to convert Event foreign keys to tags

from django.db import migrations


def migrate_events_to_tags(apps, schema_editor):
    Activity = apps.get_model('presente', 'Activity')
    Event = apps.get_model('presente', 'Event')
    Tag = apps.get_model('taggit', 'Tag')
    TaggedItem = apps.get_model('taggit', 'TaggedItem')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # Get the ContentType for Activity
    activity_content_type = ContentType.objects.get_for_model(Activity)

    # Process all activities that have an event
    for activity in Activity.objects.select_related('event').all():
        if activity.event:
            # Get or create a tag with the event name
            tag, _ = Tag.objects.get_or_create(
                name=activity.event.name,
                defaults={'slug': activity.event.name.lower().replace(' ', '-')}
            )

            # Create the TaggedItem relationship
            TaggedItem.objects.get_or_create(
                tag=tag,
                content_type=activity_content_type,
                object_id=activity.id
            )


def reverse_migration(apps, schema_editor):
    """This migration cannot be reversed as Event model will be deleted"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('presente', '0004_add_tags_field'),
        ('taggit', '0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RunPython(migrate_events_to_tags, reverse_migration),
    ]
