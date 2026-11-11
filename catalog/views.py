from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Application
from .forms import UserRegistrationForm, ApplicationCreateForm


def index(request):
    completed_apps = Application.objects.filter(status='d').order_by('-created_at')[:4]
    processing_count = Application.objects.filter(status='w').count()

    return render(request, 'catalog/index.html', {
        'completed_apps': completed_apps,
        'processing_count': processing_count
    })


def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'catalog/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    error_message = None
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
        else:
            error_message = "Неправильный логин или пароль."
    else:
        form = AuthenticationForm()
    return render(request, 'catalog/login.html', {'form': form, 'error_message': error_message})


def logout_view(request):
    logout(request)
    return redirect('index')


@login_required
def profile_view(request):
    user_apps = Application.objects.filter(user=request.user).order_by('-created_at')

    status_filter = request.GET.get('status')
    if status_filter in ['n', 'w', 'd']:
        user_apps = user_apps.filter(status=status_filter)

    return render(request, 'catalog/profile.html', {
        'user_apps': user_apps,
        'status_filter': status_filter
    })


@login_required
def application_create_view(request):
    if request.method == 'POST':
        form = ApplicationCreateForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.status = 'n'
            application.save()
            return redirect('profile')
    else:
        form = ApplicationCreateForm()
    return render(request, 'catalog/application_form.html', {'form': form})
