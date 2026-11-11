from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('application/create/', views.application_create_view, name='application-create'),
    path('application/<uuid:pk>/delete/', views.application_delete_view, name='application-delete'),
    path('admin-panel/', views.admin_panel_view, name='admin-panel'),
]
