from django import forms


class SearchForm(forms.Form):
    q = forms.CharField(max_length=150, label="Search")
    mode = forms.ChoiceField(
        choices=(
            ("all", "everywhere"),
            ("name", "in names"),
            ("id", "Lego ID"),
        ),
        widget=forms.RadioSelect,
        initial="all",
        label="",
    )
