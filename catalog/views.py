from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import UserRegistrationForm


def index(request):
    return render(request, 'catalog/base_generic.html')


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserRegistrationForm()
    return render(request, 'catalog/register.html', {'form': form})
