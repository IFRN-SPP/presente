from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import User


@receiver(post_save, sender=User)
def assign_permissions_based_on_type(sender, instance, created, **kwargs):
    from presente.models import Activity

    if instance.type == "SERVIDOR":
        # Get or create Servidor group
        servidor_group, _ = Group.objects.get_or_create(name="Servidor")

        # Add activity permissions to the group
        activity_content_type = ContentType.objects.get_for_model(Activity)
        permissions = Permission.objects.filter(content_type=activity_content_type)
        servidor_group.permissions.set(permissions)

        # Add user to Servidor group
        instance.groups.add(servidor_group)
    elif instance.type == "ALUNO":
        # Remove from Servidor group if they were in it
        try:
            servidor_group = Group.objects.get(name="Servidor")
            instance.groups.remove(servidor_group)
        except Group.DoesNotExist:
            pass
