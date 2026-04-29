from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from .models import AccountProfile
from .models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'


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
