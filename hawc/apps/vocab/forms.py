from crispy_forms import layout as cfl
from django import forms

from ..common.forms import BaseFormHelper
from . import models


class CommentForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = ("comment", "last_url_visited")
        widgets = {
            "last_url_visited": forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        last_url_visited = kwargs.pop("last_url_visited")
        super().__init__(*args, **kwargs)
        self.helper = self.setHelper()
        self.fields["last_url_visited"].initial = last_url_visited

    def setHelper(self):
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs["class"] = "col-md-12"

        inputs = {
            "legend_text": "Submit a comment",
            "help_text": """
                Submit a comment regarding the controlled vocabulary. Please be as
                descriptive as possible. We may contact you via email to better understand
                your request.
            """,
            "form_actions": [
                cfl.Submit("save", "Submit"),
                cfl.HTML(
                    """<a class="btn btn-light" href='#' onclick='window.close()'>Cancel</a>"""
                ),
            ],
        }

        helper = BaseFormHelper(self, **inputs)

        return helper
