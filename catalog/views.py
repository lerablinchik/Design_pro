from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Application, Category
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


@login_required
def application_delete_view(request, pk):
    application = get_object_or_404(Application, pk=pk)

    if application.user != request.user:
        raise PermissionDenied

    if application.status != 'n':
        return redirect('profile')

    if request.method == 'POST':
        application.delete()
        return redirect('profile')

    return render(request, 'catalog/application_confirm_delete.html', {'application': application})


@login_required
def admin_panel_view(request):
    if not request.user.is_staff:
        raise PermissionDenied

    all_apps = Application.objects.all().order_by('-created_at')
    all_categories = Category.objects.all().order_by('name')

    status_filter = request.GET.get('status')
    if status_filter in ['n', 'w', 'd']:
        all_apps = all_apps.filter(status=status_filter)

    if request.method == 'POST':
        action_type = request.POST.get('action_type')

        if action_type == 'change_status':
            app_id = request.POST.get('app_id')
            new_status = request.POST.get('new_status')
            app = get_object_or_404(Application, pk=app_id)
            app.status = new_status
            app.save()

        elif action_type == 'create_category':
            cat_name = request.POST.get('cat_name', '').strip()
            if cat_name and not Category.objects.filter(name=cat_name).exists():
                Category.objects.create(name=cat_name)

        elif action_type == 'delete_category':
            cat_id = request.POST.get('cat_id')
            cat = get_object_or_404(Category, pk=cat_id)
            cat.delete()

        return redirect('admin-panel')

    return render(request, 'catalog/admin_panel.html', {
        'all_apps': all_apps,
        'all_categories': all_categories,
        'status_filter': status_filter
    })
