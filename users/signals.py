from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def assign_group_based_on_type(sender, instance, created, **kwargs):
    """
    Automatically assign users to groups based on their type.
    SERVIDOR users get activity management permissions.
    """
    if not instance.type:
        return

    # Get or create the Servidor group
    servidor_group, _ = Group.objects.get_or_create(name="Servidor")

    if instance.type == "SERVIDOR":
        # Add user to Servidor group
        instance.groups.add(servidor_group)

        # Ensure the group has activity permissions
        from presente.models import Activity

        content_type = ContentType.objects.get_for_model(Activity)
        permissions = Permission.objects.filter(
            content_type=content_type,
            codename__in=[
                "add_activity",
                "change_activity",
                "delete_activity",
                "view_activity",
            ],
        )
        servidor_group.permissions.set(permissions)

    elif instance.type == "ALUNO":
        # Remove user from Servidor group if they're in it
        instance.groups.remove(servidor_group)
