from django.conf import settings
from django.db import models


class AccountProfile(models.Model):
    STUDENT = "student"
    TEACHER = "teacher"
    ACCOUNT_TYPE_CHOICES = [
        (STUDENT, "Student"),
        (TEACHER, "Teacher"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.get_account_type_display()})"


class Student(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    course = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    scheduled_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="managed_events",
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="joined_events",
    )

    class Meta:
        ordering = ["scheduled_at", "title"]

    def __str__(self):
        return self.title
