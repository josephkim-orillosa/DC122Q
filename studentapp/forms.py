from datetime import datetime

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import AccountProfile, Event, Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'


class EventForm(forms.ModelForm):
    HOUR_CHOICES = [(hour, datetime.strptime(str(hour), "%H").strftime("%I %p")) for hour in range(24)]
    MINUTE_CHOICES = [(minute, f"{minute:02d}") for minute in range(0, 60, 5)]

    scheduled_date = forms.DateField(
        label="Schedule Date",
        widget=forms.SelectDateWidget,
    )
    scheduled_hour = forms.ChoiceField(
        label="Schedule Hour",
        choices=HOUR_CHOICES,
    )
    scheduled_minute = forms.ChoiceField(
        label="Schedule Minute",
        choices=MINUTE_CHOICES,
    )

    class Meta:
        model = Event
        fields = ("title", "description")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        scheduled_at = self.instance.scheduled_at if self.instance and self.instance.pk else None
        if scheduled_at:
            scheduled_at = timezone.localtime(scheduled_at)
            self.fields["scheduled_date"].initial = scheduled_at.date()
            self.fields["scheduled_hour"].initial = scheduled_at.hour
            self.fields["scheduled_minute"].initial = scheduled_at.minute

    def clean(self):
        cleaned_data = super().clean()
        scheduled_date = cleaned_data.get("scheduled_date")
        scheduled_hour = cleaned_data.get("scheduled_hour")
        scheduled_minute = cleaned_data.get("scheduled_minute")

        if scheduled_date and scheduled_hour is not None and scheduled_minute is not None:
            scheduled_at = datetime.combine(
                scheduled_date,
                datetime.min.time().replace(
                    hour=int(scheduled_hour),
                    minute=int(scheduled_minute),
                ),
            )
            if timezone.is_naive(scheduled_at):
                scheduled_at = timezone.make_aware(scheduled_at)
            cleaned_data["scheduled_at"] = scheduled_at

        return cleaned_data

    def save(self, commit=True):
        event = super().save(commit=False)
        event.scheduled_at = self.cleaned_data["scheduled_at"]
        if commit:
            event.save()
            self.save_m2m()
        return event


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, help_text="")
    password = forms.CharField(widget=forms.PasswordInput, help_text="")
    error_messages = {
        "invalid_login": "Wrong username or password. Please try again.",
    }
    username = forms.CharField(widget=forms.TextInput(attrs={
        "autocomplete": "off"
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "autocomplete": "new-password"
    }))

class RegisterForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    account_type = forms.ChoiceField(choices=AccountProfile.ACCOUNT_TYPE_CHOICES)
    password = forms.CharField(widget=forms.PasswordInput, help_text="")
    

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "account_type",
            "password",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = ""

    def clean_password(self):
        password = self.cleaned_data["password"]
        password_validation.validate_password(password, self.instance)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()
            profile = user.accountprofile
            profile.account_type = self.cleaned_data["account_type"]
            profile.save()

        return user


class AccountEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    account_type = forms.ChoiceField(choices=AccountProfile.ACCOUNT_TYPE_CHOICES)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = ""
        profile, _ = AccountProfile.objects.get_or_create(
            user=self.instance,
            defaults={"account_type": AccountProfile.STUDENT},
        )
        self.fields["account_type"].initial = profile.account_type

    def save(self, commit=True):
        user = super().save(commit=commit)
        profile, _ = AccountProfile.objects.get_or_create(
            user=user,
            defaults={"account_type": AccountProfile.STUDENT},
        )
        profile.account_type = self.cleaned_data["account_type"]
        if commit:
            profile.save()
        return user
