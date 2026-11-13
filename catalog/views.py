from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Application, Category
from .forms import UserRegistrationForm, ApplicationCreateForm

#Главная стр
def index(request):
    completed_apps = Application.objects.filter(status='d').order_by('-created_at')[:4]
        #то что "Выполнено" выводит на экран, сортирует от новых к старым и ток 4 шт
    processing_count = Application.objects.filter(status='w').count()
        #счиитает скок заявок в работе

    return render(request, 'catalog/index.html', {
        'completed_apps': completed_apps,
        'processing_count': processing_count
    })

#Регистрация
def register_view(request):
    if request.user.is_authenticated: #если уже вошел то кидает в профтль
        return redirect('profile')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():  #если ошибок нет то сохраняет человека
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'catalog/register.html', {'form': form})

#Вход в аккаунт
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

#Выход
def logout_view(request):
    logout(request)   #стирает сессию пользователя
    return redirect('index') #перекидывает на главную страницу

#Мои заявки
@login_required #без входа в аккаунт сюда не попасть
def profile_view(request):
    user_apps = Application.objects.filter(user=request.user).order_by('-created_at') #берет из базы только заявки текущего пользователя

    status_filter = request.GET.get('status')
    if status_filter in ['n', 'w', 'd']:  # если выбрана вкладка (Новая, В работе или Выполнена)
        user_apps = user_apps.filter(status=status_filter) # оставляем заявки только с этим статусом

    return render(request, 'catalog/profile.html', {
        'user_apps': user_apps,
        'status_filter': status_filter
    })


@login_required
def application_create_view(request):  # страница создания новой заявки
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
def application_delete_view(request, pk): # страница удаления заявки по её номеру (pk)
    application = get_object_or_404(Application, pk=pk)

    if application.user != request.user:  # если заявку пытается удалить не её автор, запрещаем
        raise PermissionDenied

    if application.status != 'n':   # если заявка уже не «Новая»
        return redirect('profile') # удалять нельзя

    if request.method == 'POST':   # если нажали «Да, удалить» на странице подтверждения
        application.delete()
        return redirect('profile')

    return render(request, 'catalog/application_confirm_delete.html', {'application': application})


@login_required
def admin_panel_view(request):
    if not request.user.is_staff:  # если у пользователя нет прав администратора, нельзя
        raise PermissionDenied

    all_apps = Application.objects.all().order_by('-created_at')
    all_categories = Category.objects.all().order_by('name')

    status_filter = request.GET.get('status')
    if status_filter in ['n', 'w', 'd']:
        all_apps = all_apps.filter(status=status_filter)

    if request.method == 'POST':
        action_type = request.POST.get('action_type')

        if action_type == 'change_status':   # если меняем статус заявки
            app_id = request.POST.get('app_id')
            new_status = request.POST.get('new_status')
            app = get_object_or_404(Application, pk=app_id)
            app.status = new_status
            if new_status == 'd' and 'design_photo' in request.FILES:  # если статус «Выполнено» и прикрепили фото
                app.design_photo = request.FILES['design_photo']
            app.save()

        elif action_type == 'create_category':
            cat_name = request.POST.get('cat_name', '').strip()
            if cat_name and not Category.objects.filter(name=cat_name).exists():   # если название не пустое и такой категории еще нет
                Category.objects.create(name=cat_name)

        elif action_type == 'delete_category':
            cat_id = request.POST.get('cat_id')
            cat = get_object_or_404(Category, pk=cat_id)    # находим категорию в базе
            cat.delete()     # удаляем её (вместе со всеми связанными заявками)

        return redirect('admin-panel')

    return render(request, 'catalog/admin_panel.html', {
        'all_apps': all_apps,
        'all_categories': all_categories,
        'status_filter': status_filter
    })

