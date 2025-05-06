from django import forms


class SearchForm(forms.Form):
    q = forms.CharField(max_length=150, label="Search", widget=forms.SearchInput)
    mode = forms.ChoiceField(
        choices=(
            ("all", "everywhere"),
            ("name", "in names"),
            ("id", "Lego ID"),
            ("color", "in colors"),
        ),
        widget=forms.RadioSelect,
        initial="all",
        label="",
    )


class AddSetForm(forms.Form):
    set_lego_id = forms.CharField(
        max_length=28,    # after optionally adding the `-1` suffix, must not exceed
                          # max length 30 of the `LegoSet.lego_id` field
        widget=forms.TextInput(attrs={"autofocus": True}),
        label="Lego Set ID",
    )
