from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Event(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"


class Activity(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="activities",
    )
    title = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Atividade"
        verbose_name_plural = "Atividades"
