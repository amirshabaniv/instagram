from django.db import models


class TimeStamp(models.Model):
    """Abstract base model for inheriting in other tables."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True