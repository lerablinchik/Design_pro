from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import Application
from .forms import UserRegistrationForm


def index(request):
    completed_apps = Application.objects.filter(status='d').order_by('-created_at')[:4]
    processing_count = Application.objects.filter(status='w').count()

    return render(request, 'catalog/index.html', {
        'completed_apps': completed_apps,
        'processing_count': processing_count
    })


def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('index')
    else:
        form = UserRegistrationForm()
    return render(request, 'catalog/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    error_message = None
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
        else:
            error_message = "Неправильный логин или пароль."
    else:
        form = AuthenticationForm()
    return render(request, 'catalog/login.html', {'form': form, 'error_message': error_message})


def logout_view(request):
    logout(request)
    return redirect('index')
