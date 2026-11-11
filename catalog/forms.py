import re
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class UserRegistrationForm(forms.ModelForm):
    fio = forms.CharField(
        max_length=150,
        label="ФИО",
        help_text="Только кириллические буквы, дефис и пробелы"
    )
    login = forms.CharField(
        max_length=150,
        label="Логин",
        help_text="Только латиница и дефис"
    )
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput(), label="Пароль")
    password_confirm = forms.CharField(widget=forms.PasswordInput(), label="Повтор пароля")
    agreement = forms.BooleanField(label="Согласие на обработку персональных данных", required=True)

    class Meta:
        model = User
        fields = ['fio', 'login', 'email', 'password', 'password_confirm', 'agreement']

    def clean_fio(self):
        fio = self.cleaned_data.get('fio')
        if not re.match(r'^[А-Яа-яЁё\s-]+$', fio):
            raise ValidationError("ФИО должно содержать только кириллические буквы, дефис и пробелы.")
        return fio

    def clean_login(self):
        login = self.cleaned_data.get('login')
        if not re.match(r'^[A-Za-z-]+$', login):
            raise ValidationError("Логин должен содержать только латинские буквы и дефис.")

        if User.objects.filter(username=login).exists():
            raise ValidationError("Пользователь с таким логином уже существует.")
        return login

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Введенные значения должны совпадать с паролем.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['login']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['fio']
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
