from django.contrib import messages


def form_errors_to_messages(request, form):
    for _, errors in form.errors.items():
        messages.error(request, errors)
