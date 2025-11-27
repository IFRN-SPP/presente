from django import forms
from django.contrib.auth import get_user_model
from .models import Activity

User = get_user_model()


class ActivityForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        label="Tags",
        widget=forms.TextInput(
            attrs={"class": "form-control", "data-tom-select": "tags"}
        ),
        help_text="Tags para organizar as atividades (ex: 'Workshop 2024', 'Python')",
    )

    class Meta:
        model = Activity
        fields = [
            "title",
            "start_time",
            "end_time",
            "qr_timeout",
            "is_published",
            "owners",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "start_time": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "end_time": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "qr_timeout": forms.NumberInput(
                attrs={"class": "form-control", "min": "10"}
            ),
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "owners": forms.SelectMultiple(
                attrs={"class": "form-control", "data-tom-select": "users"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["start_time"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["end_time"].input_formats = ["%Y-%m-%dT%H:%M"]

        # Populate owners field with SERVIDOR users only
        self.fields["owners"].queryset = User.objects.filter(type="SERVIDOR").order_by(
            "email"
        )
        self.fields["owners"].label_from_instance = (
            lambda obj: obj.get_full_name() or obj.email
        )

        # Populate tags field with existing tags
        if self.instance and self.instance.pk:
            self.fields["tags"].initial = ", ".join(
                [tag.name for tag in self.instance.tags.all()]
            )

        # Set field order
        self.order_fields(
            [
                "title",
                "tags",
                "start_time",
                "end_time",
                "qr_timeout",
                "is_published",
                "owners",
            ]
        )

    def save(self, commit=True):
        # Save the tags data before calling super() since tags is not a model field
        tags_str = self.cleaned_data.get("tags", "")

        # Call parent save
        instance = super().save(commit=commit)

        # Handle tags only after instance is saved (requires pk)
        if instance.pk:
            if tags_str:
                tag_list = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
                instance.tags.set(tag_list)
            else:
                instance.tags.clear()

        return instance
