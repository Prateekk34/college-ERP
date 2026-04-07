from django import forms
from .models import Notice


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = [
            "title",
            "message",
            "target",
            "department",
            "course",
            "publish_date",
            "expiry_date",
            "is_active",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "target": forms.Select(attrs={"class": "form-select"}),
            "department": forms.Select(attrs={"class": "form-select"}),
            "course": forms.Select(attrs={"class": "form-select"}),
            "publish_date": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M"
            ),
            "expiry_date": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M"
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["publish_date"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["expiry_date"].input_formats = ["%Y-%m-%dT%H:%M"]

        if self.instance and self.instance.pk:
            if self.instance.publish_date:
                self.initial["publish_date"] = self.instance.publish_date.strftime("%Y-%m-%dT%H:%M")
            if self.instance.expiry_date:
                self.initial["expiry_date"] = self.instance.expiry_date.strftime("%Y-%m-%dT%H:%M")