from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class BaseRegistrationForm(UserCreationForm):
    """Shared styling and validation for learner/parent registration."""

    class Meta:
        model = User
        fields = ("username", "first_name", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].label = "Your name"
        self.fields["first_name"].required = True
        self.fields["username"].help_text = "Use 3–150 letters, numbers, or @/./+/-/_."
        self.fields["email"].label = "Email address"
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "kid-input")


class LearnerRegistrationForm(BaseRegistrationForm):
    parent_email = forms.EmailField(
        required=False,
        label="Parent / guardian email",
        help_text="Optional. It helps a parent connect the learner later.",
    )
    avatar = forms.ChoiceField(
        choices=User.AVATAR_CHOICES,
        widget=forms.RadioSelect,
        label="Pick an avatar",
    )
    age_group = forms.ChoiceField(
        choices=User.AGE_GROUP_CHOICES,
        widget=forms.RadioSelect,
        label="Age group",
    )

    class Meta(BaseRegistrationForm.Meta):
        fields = (
            "username",
            "first_name",
            "email",
            "avatar",
            "age_group",
            "parent_email",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.account_type = "learner"
        user.is_child_learner = True
        user.parent_email = self.cleaned_data.get("parent_email", "")
        user.avatar = self.cleaned_data["avatar"]
        user.age_group = self.cleaned_data["age_group"]
        if user.parent_email:
            user.parent = User.objects.filter(
                email__iexact=user.parent_email,
                account_type="parent",
                is_active=True,
            ).first()
        if commit:
            user.save()
        return user


class ParentRegistrationForm(BaseRegistrationForm):
    class Meta(BaseRegistrationForm.Meta):
        fields = ("username", "first_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.account_type = "parent"
        user.is_child_learner = False
        user.avatar = "star"
        user.age_group = ""
        if commit:
            user.save()
        return user


class ChildCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Temporary password",
        widget=forms.PasswordInput(attrs={"class": "kid-input"}),
        min_length=8,
        help_text="The child can use this password to sign in independently.",
    )
    password2 = forms.CharField(
        label="Confirm temporary password",
        widget=forms.PasswordInput(attrs={"class": "kid-input"}),
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "avatar", "age_group", "parent_email")

    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_user = parent
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "kid-input")

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            self.add_error("password2", "Passwords do not match.")
        if cleaned.get("username"):
            qs = User.objects.filter(username__iexact=cleaned["username"])
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error("username", "That username is already in use.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.account_type = "learner"
        user.is_child_learner = True
        user.parent = self.parent_user
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
