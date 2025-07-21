from .forms import SearchForm


def common_context(request):
    return {
        "website_name": "O&F Lego",
        "search_form": SearchForm,
    }
