from django import forms


class SearchForm(forms.Form):
    q = forms.CharField(max_length=150, label="Search")
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
        max_length=30,
        widget=forms.TextInput(attrs={"autofocus": True}),
        label="Lego Set ID",
    )
