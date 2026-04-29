from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AccountProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_or_update_account_profile(sender, instance, created, **kwargs):
    if created:
        AccountProfile.objects.get_or_create(
            user=instance,
            defaults={"account_type": AccountProfile.STUDENT},
        )
        return

    AccountProfile.objects.get_or_create(
        user=instance,
        defaults={"account_type": AccountProfile.STUDENT},
    )
