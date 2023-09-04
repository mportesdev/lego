from django import forms
from django.utils.translation import gettext_lazy as _


class SearchForm(forms.Form):
    q = forms.CharField(max_length=150, label=_("Search"))
    mode = forms.ChoiceField(
        choices=(
            ("all", _("everywhere")),
            ("name", _("in names")),
            ("id", _("Lego ID")),
            ("color", _("in colors")),
        ),
        widget=forms.RadioSelect,
        initial="all",
        label="",
    )


class AddSetForm(forms.Form):
    set_lego_id = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"autofocus": True}),
        label=_("Lego Set ID"),
    )
